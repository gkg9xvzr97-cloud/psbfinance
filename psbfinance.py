import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

export default function FinanceFailuresAnalytics() {
  const sampleData = [
    { name: "2019", value: 120 },
    { name: "2020", value: 80 },
    { name: "2021", value: 150 },
    { name: "2022", value: 60 },
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6 space-y-8">
      <header className="text-center">
        <h1 className="text-4xl font-bold">Finance Failures Analytics</h1>
        <p className="text-gray-600 mt-2">Analyze failed companies, unpopular investments, and failed financial models</p>
      </header>

      <section className="grid md:grid-cols-2 gap-6">
        <Card className="shadow-xl rounded-2xl">
          <CardContent className="p-6">
            <h2 className="text-2xl font-semibold mb-4">Failed Companies</h2>
            <p className="text-gray-700 mb-4">A database of major companies that collapsed due to financial mismanagement, fraud, or poor strategy.</p>
            <Button>View Companies</Button>
          </CardContent>
        </Card>

        <Card className="shadow-xl rounded-2xl">
          <CardContent className="p-6">
            <h2 className="text-2xl font-semibold mb-4">Unpopular Investments</h2>
            <p className="text-gray-700 mb-4">Explore assets that are avoided by investors and analyze their risks and returns.</p>
            <Button>Explore</Button>
          </CardContent>
        </Card>
      </section>

      <section className="p-6 bg-white rounded-2xl shadow-xl">
        <h2 className="text-2xl font-semibold mb-6">Sample Index Comparison Chart</h2>
        <LineChart width={600} height={300} data={sampleData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="value" stroke="black" />
        </LineChart>
      </section>

      <section className="p-6 bg-white rounded-2xl shadow-xl">
        <h2 className="text-2xl font-semibold mb-6">Latest Finance News</h2>
        <p>Dynamic news feed will be integrated here using a news API.</p>
      </section>

      <footer className="text-center text-gray-600 mt-12">
        <p>© 2025 Finance Failures Analytics | Built for Tech for Business</p>
      </footer>
    </div>
  );
}
