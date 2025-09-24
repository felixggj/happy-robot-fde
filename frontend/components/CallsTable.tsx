"use client";

import { useState, useEffect } from "react";
import { getCallSessions } from "@/lib/api";

interface CallSession {
  session_id: string;
  carrier_mc: string;
  carrier_name: string;
  load_id: string;
  initial_rate: number;
  negotiated_rate: number | null;
  negotiation_rounds: number;
  outcome: string;
  sentiment: string;
  call_duration: number;
  created_at: string;
}

interface CallsTableProps {
  outcomes: Record<string, number>;
  sentiment: Record<string, number>;
}

export function CallsTable({}: CallsTableProps) {
  const [callSessions, setCallSessions] = useState<CallSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCallSessions = async () => {
      try {
        setLoading(true);
        setError(null);
        const sessions = await getCallSessions(10); // Limit to 10 recent sessions
        setCallSessions(sessions);
      } catch (err) {
        setError("Failed to fetch call sessions");
        console.error("Error fetching call sessions:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchCallSessions();
  }, []);

  const getOutcomeColor = (outcome: string) => {
    switch (outcome) {
      case "accepted":
        return "bg-green-100 text-green-800";
      case "rejected":
        return "bg-red-100 text-red-800";
      case "negotiating":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "positive":
        return "bg-green-100 text-green-800";
      case "negative":
        return "bg-red-100 text-red-800";
      case "neutral":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-100 p-4">
        <div className="animate-pulse">
          <div className="h-3 bg-gray-200 rounded w-1/4 mb-3"></div>
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-3 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-100">
      <div className="px-4 py-3 border-b border-gray-100">
        <h3 className="text-sm font-medium text-gray-900">
          Recent Call Sessions
        </h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50/50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Carrier
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                MC Number
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Outcome
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rate
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rounds
              </th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Sentiment
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {callSessions.map((session) => (
              <tr key={session.session_id} className="hover:bg-gray-50/50">
                <td className="px-4 py-1.5 whitespace-nowrap">
                  <div className="text-xs text-gray-900">
                    {session.carrier_name}
                  </div>
                </td>
                <td className="px-4 py-1.5 whitespace-nowrap">
                  <div className="text-xs text-gray-900">
                    {session.carrier_mc}
                  </div>
                </td>
                <td className="px-4 py-1.5 whitespace-nowrap">
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-medium ${getOutcomeColor(
                      session.outcome
                    )}`}
                  >
                    {session.outcome?.charAt(0).toUpperCase() +
                      session.outcome?.slice(1)}
                  </span>
                </td>
                <td className="px-4 py-1.5 whitespace-nowrap">
                  <div className="text-xs text-gray-900">
                    {session.negotiated_rate
                      ? `$${(session.negotiated_rate || 0).toLocaleString()}`
                      : `$${(session.initial_rate || 0).toLocaleString()}`}
                  </div>
                </td>
                <td className="px-4 py-1.5 whitespace-nowrap">
                  <div className="text-xs text-gray-900">
                    {session.negotiation_rounds || 0}
                  </div>
                </td>
                <td className="px-4 py-1.5 whitespace-nowrap">
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-medium ${getSentimentColor(
                      session.sentiment
                    )}`}
                  >
                    {session.sentiment?.charAt(0).toUpperCase() +
                      session.sentiment?.slice(1)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
