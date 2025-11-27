import { Button } from "@/components/ui/button";
import confetti from "canvas-confetti";
import type { Options as ConfettiOptions } from "canvas-confetti";

interface ConfettiButtonProps {
  options?: ConfettiOptions;
  children: React.ReactNode;
  className?: string;
}

export function ConfettiButton({
  options,
  children,
  className,
}: ConfettiButtonProps) {
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    const target = event.currentTarget;
    const rect = target.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;

    confetti({
      ...options,
      origin: {
        x: x / window.innerWidth,
        y: y / window.innerHeight,
      },
    });
  };

  return (
    <Button onClick={handleClick} className={className}>
      {children}
    </Button>
  );
}
