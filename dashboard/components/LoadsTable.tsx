"use client";

import { useState, useEffect } from "react";
import { getLoads } from "@/lib/api";
import { Truck, MapPin, Calendar, Package } from "lucide-react";

interface Load {
  load_id: string;
  origin: string;
  destination: string;
  pickup_datetime: string;
  delivery_datetime: string;
  equipment_type: string;
  loadboard_rate: number;
  notes?: string;
  weight?: number;
  commodity_type?: string;
  num_of_pieces?: number;
  miles?: number;
  dimensions?: string;
  score: number;
}

export function LoadsTable() {
  const [loads, setLoads] = useState<Load[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchLoads() {
      try {
        const data = await getLoads();
        setLoads(data);
      } catch (err) {
        setError("Failed to fetch loads");
        console.error("Error fetching loads:", err);
      } finally {
        setLoading(false);
      }
    }

    fetchLoads();
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-4 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="text-red-600 text-center">{error}</div>
      </div>
    );
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateString;
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-100">
      <div className="px-4 py-3 border-b border-gray-100">
        <h3 className="text-sm font-medium text-gray-900 flex items-center">
          <Truck className="h-4 w-4 mr-2 text-gray-600" />
          Available Loads
        </h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50/50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Load ID
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Route
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Equipment
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Pickup
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rate
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Details
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {loads.map((load) => (
              <tr key={load.load_id} className="hover:bg-gray-50/50">
                <td className="px-4 py-2 whitespace-nowrap">
                  <div className="text-xs font-medium text-gray-900">
                    {load.load_id}
                  </div>
                </td>
                <td className="px-4 py-2">
                  <div className="flex items-center">
                    <MapPin className="h-3 w-3 text-gray-400 mr-1.5" />
                    <div>
                      <div className="text-xs font-medium text-gray-900">
                        {load.origin} → {load.destination}
                      </div>
                      {load.miles && (
                        <div className="text-xs text-gray-400">
                          {load.miles} miles
                        </div>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-4 py-2 whitespace-nowrap">
                  <div className="flex items-center">
                    <Package className="h-3 w-3 text-gray-400 mr-1.5" />
                    <div>
                      <div className="text-xs text-gray-900">
                        {load.equipment_type}
                      </div>
                      {load.commodity_type && (
                        <div className="text-xs text-gray-500">
                          {load.commodity_type}
                        </div>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-4 py-2 whitespace-nowrap">
                  <div className="flex items-center">
                    <Calendar className="h-3 w-3 text-gray-400 mr-1.5" />
                    <div className="text-xs text-gray-900">
                      {formatDate(load.pickup_datetime)}
                    </div>
                  </div>
                </td>
                <td className="px-4 py-2 whitespace-nowrap">
                  <div className="text-xs font-semibold text-green-600">
                    {formatCurrency(load.loadboard_rate)}
                  </div>
                </td>
                <td className="px-4 py-2">
                  <div className="text-xs text-gray-900 space-y-0.5">
                    {load.weight && (
                      <div className="text-gray-500">
                        {load.weight.toLocaleString()} lbs
                      </div>
                    )}
                    {load.num_of_pieces && (
                      <div className="text-gray-500">
                        {load.num_of_pieces} pieces
                      </div>
                    )}
                    {load.dimensions && (
                      <div className="text-gray-500">{load.dimensions}</div>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {loads.length === 0 && (
        <div className="text-center py-12">
          <Truck className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No loads available at the moment</p>
        </div>
      )}
    </div>
  );
}
