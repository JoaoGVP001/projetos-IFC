import {
  useEffect,
  useRef,
  useState,
  type ButtonHTMLAttributes,
  type ReactNode,
} from "react";
import { createPortal } from "react-dom";
import { MoreHorizontal, X, LoaderCircle, type LucideIcon } from "lucide-react";
export function Button({
  children,
  className = "",
  variant = "soft",
  icon: Icon,
  ...p
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "soft" | "primary" | "ghost" | "danger";
  icon?: LucideIcon;
}) {
  return (
    <button type="button" className={`btn btn-${variant} ${className}`} {...p}>
      {Icon && <Icon size={17} />}
      {children}
    </button>
  );
}
export function Badge({
  children,
  kind = "neutral",
}: {
  children: ReactNode;
  kind?: string;
}) {
  return <span className={`badge badge-${kind}`}>{children}</span>;
}
export function Empty({
  icon: Icon,
  title,
  children,
  action,
}: {
  icon: LucideIcon;
  title: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="empty">
      <div className="empty-icon">
        <Icon size={28} />
      </div>
      <h2>{title}</h2>
      <p>{children}</p>
      {action}
    </div>
  );
}
export function Dialog({
  title,
  subtitle,
  children,
  onClose,
  wide = false,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  onClose: () => void;
  wide?: boolean;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const old = document.activeElement as HTMLElement;
    ref.current?.showModal();
    return () => {
      ref.current?.close();
      old?.focus?.();
    };
  }, []);
  return createPortal(
    <dialog
      ref={ref}
      className={`dialog ${wide ? "dialog-wide" : ""}`}
      onCancel={(e) => {
        e.preventDefault();
        onClose();
      }}
      onClick={(e) => {
        if (e.target === ref.current) onClose();
      }}
    >
      <div className="dialog-shell">
        <header>
          <div>
            <h2>{title}</h2>
            {subtitle && <p>{subtitle}</p>}
          </div>
          <Button variant="ghost" aria-label="Fechar diálogo" onClick={onClose}>
            <X size={20} />
          </Button>
        </header>
        <div className="dialog-body">{children}</div>
      </div>
    </dialog>,
    document.body,
  );
}
export function Field({
  label,
  children,
  hint,
}: {
  label: string;
  children: ReactNode;
  hint?: string;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
      {hint && <small>{hint}</small>}
    </label>
  );
}
export function Menu({
  label,
  items,
  disabled = false,
}: {
  label: string;
  items: {
    label: string;
    icon?: LucideIcon;
    danger?: boolean;
    action: () => void;
  }[];
  disabled?: boolean;
}) {
  const [place, setPlace] = useState<{ x: number; y: number } | null>(null);
  const ref = useRef<HTMLDivElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    if (!place) return;
    const close = (e: PointerEvent) => {
      if (
        !ref.current?.contains(e.target as Node) &&
        !trigger.current?.contains(e.target as Node)
      )
        setPlace(null);
    };
    document.addEventListener("pointerdown", close);
    ref.current?.querySelector("button")?.focus();
    return () => document.removeEventListener("pointerdown", close);
  }, [place]);
  return (
    <>
      <button
        ref={trigger}
        type="button"
        className="menu-trigger"
        aria-label={label}
        aria-expanded={!!place}
        disabled={disabled}
        onClick={() => {
          const r = trigger.current!.getBoundingClientRect();
          setPlace(
            place
              ? null
              : {
                  x: Math.max(8, Math.min(innerWidth - 240, r.right - 226)),
                  y: Math.max(
                    8,
                    Math.min(
                      innerHeight - items.length * 37 - 24,
                      r.bottom + 5,
                    ),
                  ),
                },
          );
        }}
      >
        <MoreHorizontal size={18} />
      </button>
      {place &&
        createPortal(
          <div
            ref={ref}
            role="menu"
            aria-label={label}
            className="menu"
            style={{ left: place.x, top: place.y }}
            onKeyDown={(e) => {
              if (e.key === "Escape") {
                setPlace(null);
                trigger.current?.focus();
              }
              if (["ArrowDown", "ArrowUp", "Home", "End"].includes(e.key)) {
                e.preventDefault();
                const bs = Array.from(ref.current!.querySelectorAll("button"));
                const i = bs.indexOf(
                  document.activeElement as HTMLButtonElement,
                );
                bs[
                  e.key === "Home"
                    ? 0
                    : e.key === "End"
                      ? bs.length - 1
                      : (i + (e.key === "ArrowDown" ? 1 : -1) + bs.length) %
                        bs.length
                ]?.focus();
              }
            }}
          >
            {items.map(({ label, icon: Icon, action, danger }) => (
              <button
                role="menuitem"
                key={label}
                className={danger ? "danger-text" : ""}
                onClick={() => {
                  setPlace(null);
                  action();
                }}
              >
                {Icon && <Icon size={16} />}
                <span>{label}</span>
              </button>
            ))}
          </div>,
          document.body,
        )}
    </>
  );
}
export function Loading({
  children = "Carregando…",
}: {
  children?: ReactNode;
}) {
  return (
    <span className="loading">
      <LoaderCircle size={17} className="spin" />
      {children}
    </span>
  );
}
export async function copiar(texto: string) {
  try {
    await navigator.clipboard.writeText(texto);
  } catch {
    const input = document.createElement("textarea");
    input.value = texto;
    document.body.appendChild(input);
    input.select();
    const ok = document.execCommand("copy");
    input.remove();
    if (!ok)
      throw new Error(
        "Não foi possível copiar. Selecione o texto manualmente.",
      );
  }
}
