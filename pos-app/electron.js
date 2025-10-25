// electron.js - Electron main process entry point for the barber POS application
// ملف التشغيل الرئيسي لإلكتورن الخاص بتطبيق نقاط البيع وإدارة صالون الحلاقة

const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const path = require("path");
const fs = require("fs");
const isDev = !app.isPackaged;

// قاعدة البيانات عبر better-sqlite3 لضمان الأداء العالي بدون اتصال إنترنت
const Database = require("better-sqlite3");
const bcrypt = require("bcryptjs");
const { parse } = require("papaparse");
const XLSX = require("xlsx");

const dbPath = path.join(app.getPath("userData"), "database.db");
let db;

function initializeDatabase() {
  const exists = fs.existsSync(dbPath);
  db = new Database(dbPath);

  db.pragma("journal_mode = WAL");

  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      role TEXT NOT NULL DEFAULT 'admin'
    );

    CREATE TABLE IF NOT EXISTS settings (
      id INTEGER PRIMARY KEY CHECK (id = 1),
      language TEXT DEFAULT 'ar',
      currency TEXT DEFAULT 'SAR',
      taxRate REAL DEFAULT 0.15,
      storeName TEXT DEFAULT 'صالون الأناقة',
      logoPath TEXT,
      receiptType TEXT DEFAULT 'thermal'
    );

    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      barcode TEXT UNIQUE,
      price REAL NOT NULL,
      cost REAL DEFAULT 0,
      quantity INTEGER DEFAULT 0,
      lowStockThreshold INTEGER DEFAULT 5,
      category TEXT,
      image TEXT
    );

    CREATE TABLE IF NOT EXISTS customers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      phone TEXT,
      email TEXT,
      notes TEXT
    );

    CREATE TABLE IF NOT EXISTS suppliers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      phone TEXT,
      email TEXT,
      notes TEXT
    );

    CREATE TABLE IF NOT EXISTS expenses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      amount REAL NOT NULL,
      createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
      notes TEXT
    );

    CREATE TABLE IF NOT EXISTS sales (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      customerId INTEGER,
      total REAL NOT NULL,
      discount REAL DEFAULT 0,
      tax REAL DEFAULT 0,
      paymentMethod TEXT DEFAULT 'cash',
      paidAmount REAL DEFAULT 0,
      changeAmount REAL DEFAULT 0,
      userId INTEGER,
      createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (customerId) REFERENCES customers(id),
      FOREIGN KEY (userId) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS sale_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      saleId INTEGER NOT NULL,
      productId INTEGER NOT NULL,
      quantity INTEGER NOT NULL,
      price REAL NOT NULL,
      FOREIGN KEY (saleId) REFERENCES sales(id),
      FOREIGN KEY (productId) REFERENCES products(id)
    );
  `);

  if (!exists) {
    const passwordHash = bcrypt.hashSync("password", 10);
    db.prepare("INSERT INTO users (username, password, role) VALUES (?, ?, ?)").run("admin", passwordHash, "admin");
    db.prepare("INSERT OR REPLACE INTO settings (id, language, currency, taxRate, storeName) VALUES (1, 'ar', 'SAR', 0.15, 'صالون الأناقة')").run();

    const productStmt = db.prepare(`INSERT INTO products (name, barcode, price, cost, quantity, lowStockThreshold, category) VALUES (?, ?, ?, ?, ?, ?, ?)`);
    const sampleProducts = [
      ["قص شعر كلاسيكي", "1110001", 35, 10, 20, 5, "خدمات"],
      ["حلاقة ذقن", "1110002", 25, 8, 15, 5, "خدمات"],
      ["مجموعة عناية باللحية", "1110003", 60, 30, 10, 3, "منتجات"],
      ["شمع حلاقة", "1110004", 20, 5, 25, 6, "منتجات"],
      ["كريم ترطيب", "1110005", 40, 15, 12, 4, "منتجات"]
    ];
    sampleProducts.forEach((p) => productStmt.run(...p));

    const customerId = db.prepare("INSERT INTO customers (name, phone, notes) VALUES (?, ?, ?)").run("عميل تجريبي", "0500000000", "أهلاً بك").lastInsertRowid;

    const saleId = db
      .prepare(
        "INSERT INTO sales (customerId, total, discount, tax, paymentMethod, paidAmount, changeAmount, userId) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
      )
      .run(customerId, 100, 5, 15, "cash", 120, 20, 1).lastInsertRowid;

    db.prepare("INSERT INTO sale_items (saleId, productId, quantity, price) VALUES (?, ?, ?, ?)").run(saleId, 1, 1, 35);
    db.prepare("INSERT INTO sale_items (saleId, productId, quantity, price) VALUES (?, ?, ?, ?)").run(saleId, 3, 1, 60);

    db.prepare("INSERT INTO expenses (title, amount, notes) VALUES (?, ?, ?)").run("مناديل", 15, "شراء مناديل ورقية");
  }
}

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1100,
    minHeight: 720,
    backgroundColor: "#dfe7ef",
    title: "POS Barber Suite",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  if (isDev) {
    mainWindow.loadURL("http://localhost:5173");
    mainWindow.webContents.openDevTools({ mode: "detach" });
  } else {
    mainWindow.loadFile(path.join(__dirname, "dist", "index.html"));
  }
}

app.whenReady().then(() => {
  initializeDatabase();
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

// Helper utilities
function runQuery(sql, params = []) {
  return db.prepare(sql).all(...params);
}

function runGet(sql, params = []) {
  return db.prepare(sql).get(...params);
}

function runExecute(sql, params = []) {
  return db.prepare(sql).run(...params);
}

// مصادقة المستخدمين
ipcMain.handle("auth/login", (_event, credentials) => {
  const user = runGet("SELECT * FROM users WHERE username = ?", [credentials.username]);
  if (!user) {
    return { success: false, message: "المستخدم غير موجود" };
  }

  const isValid = bcrypt.compareSync(credentials.password, user.password);
  if (!isValid) {
    return { success: false, message: "كلمة المرور غير صحيحة" };
  }

  const { password, ...safeUser } = user;
  return { success: true, user: safeUser };
});

// لوحة المعلومات
ipcMain.handle("dashboard/metrics", () => {
  const today = runGet(
    "SELECT IFNULL(SUM(total), 0) as total, COUNT(*) as orders FROM sales WHERE date(createdAt) = date('now')"
  );
  const month = runGet(
    "SELECT IFNULL(SUM(total), 0) as total, COUNT(*) as orders FROM sales WHERE strftime('%Y-%m', createdAt) = strftime('%Y-%m','now')"
  );
  const expenses = runGet(
    "SELECT IFNULL(SUM(amount), 0) as total FROM expenses WHERE strftime('%Y-%m', createdAt) = strftime('%Y-%m','now')"
  );
  const topProducts = runQuery(
    `SELECT p.name, SUM(si.quantity) as qty
     FROM sale_items si
     JOIN products p ON p.id = si.productId
     GROUP BY p.name
     ORDER BY qty DESC
     LIMIT 5`
  );
  const salesTrend = runQuery(
    `SELECT strftime('%Y-%m-%d', createdAt) as day, SUM(total) as total
     FROM sales
     WHERE createdAt >= date('now', '-14 day')
     GROUP BY day
     ORDER BY day`
  );

  return { today, month, expenses, topProducts, salesTrend };
});

// البحث عن المنتجات
ipcMain.handle("pos/searchProducts", (_event, query) => {
  if (!query) {
    return runQuery("SELECT * FROM products ORDER BY name LIMIT 25");
  }
  return runQuery("SELECT * FROM products WHERE name LIKE ? OR barcode LIKE ? ORDER BY name LIMIT 25", [`%${query}%`, `%${query}%`]);
});

// إنشاء فاتورة جديدة
ipcMain.handle("pos/createSale", (_event, payload) => {
  const { items, discount, taxRate, paymentMethod, paidAmount, customerId, userId } = payload;
  const subtotal = items.reduce((acc, item) => acc + item.price * item.quantity, 0);
  const discountValue = discount || 0;
  const taxValue = (subtotal - discountValue) * taxRate;
  const total = subtotal - discountValue + taxValue;
  const changeAmount = paidAmount - total;

  const insertSale = db.prepare(
    `INSERT INTO sales (customerId, total, discount, tax, paymentMethod, paidAmount, changeAmount, userId)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
  );
  const saleId = insertSale.run(customerId || null, total, discountValue, taxValue, paymentMethod, paidAmount, changeAmount, userId).lastInsertRowid;

  const insertItem = db.prepare(
    "INSERT INTO sale_items (saleId, productId, quantity, price) VALUES (?, ?, ?, ?)"
  );
  const updateStock = db.prepare("UPDATE products SET quantity = quantity - ? WHERE id = ?");

  const transaction = db.transaction((saleItems) => {
    saleItems.forEach((item) => {
      insertItem.run(saleId, item.id, item.quantity, item.price);
      updateStock.run(item.quantity, item.id);
    });
  });

  transaction(items);

  return { saleId, total, taxValue, discountValue, changeAmount };
});

// إدارة المنتجات
ipcMain.handle("products/list", () => {
  return runQuery("SELECT * FROM products ORDER BY name COLLATE NOCASE", []);
});

ipcMain.handle("products/save", (_event, product) => {
  if (product.id) {
    runExecute(
      `UPDATE products SET name = ?, barcode = ?, price = ?, cost = ?, quantity = ?, lowStockThreshold = ?, category = ?, image = ? WHERE id = ?`,
      [product.name, product.barcode, product.price, product.cost, product.quantity, product.lowStockThreshold, product.category, product.image, product.id]
    );
    return { id: product.id };
  }
  const result = runExecute(
    `INSERT INTO products (name, barcode, price, cost, quantity, lowStockThreshold, category, image) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
    [product.name, product.barcode, product.price, product.cost, product.quantity, product.lowStockThreshold, product.category, product.image]
  );
  return { id: result.lastInsertRowid };
});

ipcMain.handle("products/delete", (_event, id) => {
  runExecute("DELETE FROM products WHERE id = ?", [id]);
  return { success: true };
});

ipcMain.handle("products/importCsv", async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    properties: ["openFile"],
    filters: [{ name: "CSV", extensions: ["csv"] }]
  });
  if (canceled || !filePaths.length) return { success: false };
  const content = fs.readFileSync(filePaths[0], "utf-8");
  const parsed = parse(content, { header: true, skipEmptyLines: true });
  const insert = db.prepare(
    `INSERT INTO products (name, barcode, price, cost, quantity, lowStockThreshold, category) VALUES (?, ?, ?, ?, ?, ?, ?)`
  );
  const transaction = db.transaction((rows) => {
    rows.forEach((row) => {
      insert.run(row.name, row.barcode, Number(row.price || 0), Number(row.cost || 0), Number(row.quantity || 0), Number(row.lowStockThreshold || 5), row.category || "");
    });
  });
  transaction(parsed.data);
  return { success: true, imported: parsed.data.length };
});

ipcMain.handle("products/exportCsv", async () => {
  const products = runQuery("SELECT * FROM products");
  const csvContent = [Object.keys(products[0] || {}).join(",")]
    .concat(products.map((p) => Object.values(p).join(",")))
    .join("\n");
  const { filePath } = await dialog.showSaveDialog({
    defaultPath: "products.csv",
    filters: [{ name: "CSV", extensions: ["csv"] }]
  });
  if (!filePath) return { success: false };
  fs.writeFileSync(filePath, csvContent, "utf-8");
  return { success: true, filePath };
});

// العملاء والموردون
ipcMain.handle("contacts/list", (_event, type) => {
  const table = type === "supplier" ? "suppliers" : "customers";
  return runQuery(`SELECT * FROM ${table} ORDER BY name`);
});

ipcMain.handle("contacts/save", (_event, payload) => {
  const table = payload.type === "supplier" ? "suppliers" : "customers";
  if (payload.data.id) {
    runExecute(`UPDATE ${table} SET name = ?, phone = ?, email = ?, notes = ? WHERE id = ?`, [payload.data.name, payload.data.phone, payload.data.email, payload.data.notes, payload.data.id]);
    return { id: payload.data.id };
  }
  const result = runExecute(`INSERT INTO ${table} (name, phone, email, notes) VALUES (?, ?, ?, ?)`, [payload.data.name, payload.data.phone, payload.data.email, payload.data.notes]);
  return { id: result.lastInsertRowid };
});

ipcMain.handle("contacts/delete", (_event, payload) => {
  const table = payload.type === "supplier" ? "suppliers" : "customers";
  runExecute(`DELETE FROM ${table} WHERE id = ?`, [payload.id]);
  return { success: true };
});

ipcMain.handle("contacts/export", async (_event, type) => {
  const table = type === "supplier" ? "suppliers" : "customers";
  const rows = runQuery(`SELECT * FROM ${table}`);
  const worksheet = XLSX.utils.json_to_sheet(rows);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, table);
  const { filePath } = await dialog.showSaveDialog({
    defaultPath: `${table}.xlsx`,
    filters: [{ name: "Excel", extensions: ["xlsx"] }]
  });
  if (!filePath) return { success: false };
  XLSX.writeFile(workbook, filePath);
  return { success: true, filePath };
});

// المصروفات
ipcMain.handle("expenses/list", () => {
  return runQuery("SELECT * FROM expenses ORDER BY datetime(createdAt) DESC");
});

ipcMain.handle("expenses/save", (_event, expense) => {
  if (expense.id) {
    runExecute("UPDATE expenses SET title = ?, amount = ?, notes = ? WHERE id = ?", [expense.title, expense.amount, expense.notes, expense.id]);
    return { id: expense.id };
  }
  const result = runExecute("INSERT INTO expenses (title, amount, notes) VALUES (?, ?, ?)", [expense.title, expense.amount, expense.notes]);
  return { id: result.lastInsertRowid };
});

ipcMain.handle("expenses/delete", (_event, id) => {
  runExecute("DELETE FROM expenses WHERE id = ?", [id]);
  return { success: true };
});

// التقارير
ipcMain.handle("reports/sales", (_event, payload) => {
  const { from, to, userId } = payload;
  let query = "SELECT s.*, u.username FROM sales s LEFT JOIN users u ON u.id = s.userId WHERE date(createdAt) BETWEEN date(?) AND date(?)";
  const params = [from, to];
  if (userId) {
    query += " AND s.userId = ?";
    params.push(userId);
  }
  return runQuery(query + " ORDER BY datetime(createdAt) DESC", params);
});

ipcMain.handle("reports/export", async (_event, payload) => {
  const rows = payload.rows || [];
  if (!rows.length) return { success: false, message: "لا توجد بيانات" };
  if (payload.type === "excel") {
    const worksheet = XLSX.utils.json_to_sheet(rows);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Sales");
    const { filePath } = await dialog.showSaveDialog({ defaultPath: "sales-report.xlsx", filters: [{ name: "Excel", extensions: ["xlsx"] }] });
    if (!filePath) return { success: false };
    XLSX.writeFile(workbook, filePath);
    return { success: true, filePath };
  }
  const { filePath } = await dialog.showSaveDialog({ defaultPath: "sales-report.json", filters: [{ name: "JSON", extensions: ["json"] }] });
  if (!filePath) return { success: false };
  fs.writeFileSync(filePath, JSON.stringify(rows, null, 2), "utf-8");
  return { success: true, filePath };
});

// الإعدادات
ipcMain.handle("settings/get", () => {
  return runGet("SELECT * FROM settings WHERE id = 1");
});

ipcMain.handle("settings/save", (_event, settings) => {
  runExecute(
    `INSERT INTO settings (id, language, currency, taxRate, storeName, logoPath, receiptType)
     VALUES (1, ?, ?, ?, ?, ?, ?)
     ON CONFLICT(id) DO UPDATE SET language = excluded.language, currency = excluded.currency, taxRate = excluded.taxRate, storeName = excluded.storeName, logoPath = excluded.logoPath, receiptType = excluded.receiptType`,
    [settings.language, settings.currency, settings.taxRate, settings.storeName, settings.logoPath, settings.receiptType]
  );
  return { success: true };
});

ipcMain.handle("settings/uploadLogo", async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog({ properties: ["openFile"], filters: [{ name: "Images", extensions: ["png", "jpg", "jpeg"] }] });
  if (canceled || !filePaths.length) return { success: false };
  const logoPath = filePaths[0];
  runExecute("UPDATE settings SET logoPath = ? WHERE id = 1", [logoPath]);
  return { success: true, logoPath };
});

// المستخدمون والصلاحيات
ipcMain.handle("users/list", () => {
  const users = runQuery("SELECT id, username, role FROM users ORDER BY username");
  return users;
});

ipcMain.handle("users/save", (_event, user) => {
  if (user.id) {
    if (user.password) {
      const hash = bcrypt.hashSync(user.password, 10);
      runExecute("UPDATE users SET username = ?, role = ?, password = ? WHERE id = ?", [user.username, user.role, hash, user.id]);
    } else {
      runExecute("UPDATE users SET username = ?, role = ? WHERE id = ?", [user.username, user.role, user.id]);
    }
    return { id: user.id };
  }
  const hash = bcrypt.hashSync(user.password || "password", 10);
  const result = runExecute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", [user.username, hash, user.role]);
  return { id: result.lastInsertRowid };
});

ipcMain.handle("users/delete", (_event, id) => {
  runExecute("DELETE FROM users WHERE id = ?", [id]);
  return { success: true };
});
