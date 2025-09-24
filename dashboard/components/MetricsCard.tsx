import { LucideIcon } from "lucide-react";

interface MetricsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  className?: string;
}

export function MetricsCard({
  title,
  value,
  subtitle,
  icon: Icon,
  className = "",
}: MetricsCardProps) {
  return (
    <div
      className={`bg-white rounded-lg border border-gray-100 p-6 ${className}`}
    >
      <div className="flex items-center space-x-4">
        <div className="p-2 bg-gray-50 rounded-lg">
          <Icon className="h-5 w-5 text-gray-700" />
        </div>
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-xl font-semibold text-gray-900">{value}</p>
          {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
        </div>
      </div>
    </div>
  );
}
