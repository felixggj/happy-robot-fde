"use client";

import { useState, useEffect } from "react";
import { getMetrics, getHealthStatus } from "@/lib/api";
import { MetricsCard } from "@/components/MetricsCard";
import { LoadsTable } from "@/components/LoadsTable";
import { CallsTable } from "@/components/CallsTable";
import {
  Phone,
  TrendingUp,
  Users,
  DollarSign,
  AlertCircle,
} from "lucide-react";

interface Metrics {
  total_calls: number;
  conversion_rate: number;
  avg_negotiation_rounds: number;
  outcomes: Record<string, number>;
  sentiment: Record<string, number>;
  total_revenue: number;
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [isHealthy, setIsHealthy] = useState<boolean>(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Check API health
      try {
        await getHealthStatus();
        setIsHealthy(true);
      } catch {
        setIsHealthy(false);
      }

      // Fetch metrics
      const metricsData = await getMetrics();
      setMetrics(metricsData);
      setLastUpdated(new Date());
    } catch (err) {
      setError("Failed to fetch dashboard data");
      console.error("Dashboard error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading && !metrics) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-600 border-t-transparent mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-8">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                HappyRobot Dashboard
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Carrier Sales Analytics
              </p>
            </div>
            <div className="flex items-center">
              <div
                className={`h-1.5 w-1.5 rounded-full mr-2 ${
                  isHealthy ? "bg-green-500" : "bg-red-500"
                }`}
              ></div>
              <span className="text-xs text-gray-500">
                {isHealthy ? "Connected" : "Offline"}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <MetricsCard
            title="Total Calls"
            value={metrics?.total_calls || 0}
            subtitle="Inbound calls"
            icon={Phone}
          />
          <MetricsCard
            title="Conversion Rate"
            value={`${metrics?.conversion_rate || 0}%`}
            subtitle="Successful bookings"
            icon={TrendingUp}
          />
          <MetricsCard
            title="Avg Rounds"
            value={metrics?.avg_negotiation_rounds || 0}
            subtitle="Negotiation rounds"
            icon={Users}
          />
          <MetricsCard
            title="Accepted Loads"
            value={metrics?.outcomes.accepted || 0}
            subtitle="Loads confirmed"
            icon={Users}
          />
          <MetricsCard
            title="Revenue Impact"
            value={`$${(metrics?.total_revenue || 0).toLocaleString()}`}
            subtitle="Total revenue"
            icon={DollarSign}
          />
        </div>

        {/* Call Sessions */}
        {metrics && (
          <div className="mb-8">
            <CallsTable
              outcomes={metrics.outcomes}
              sentiment={metrics.sentiment}
            />
          </div>
        )}

        {/* Loads Table */}
        <div className="mb-8">
          <LoadsTable />
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-gray-400 mt-8">
          <p>Last updated: {lastUpdated.toLocaleTimeString()}</p>
        </div>
      </div>
    </div>
  );
}
