import clsx from "classnames";
import { ButtonHTMLAttributes, DetailedHTMLProps } from "react";

export default function GlassButton({ className, ...props }: DetailedHTMLProps<ButtonHTMLAttributes<HTMLButtonElement>, HTMLButtonElement>) {
  return (
    <button
      className={clsx(
        "glass-button px-5 py-3 font-semibold text-primary-dark hover:text-primary-dark focus:outline-none focus:ring-2 focus:ring-primary-light",
        className
      )}
      {...props}
    />
  );
}
