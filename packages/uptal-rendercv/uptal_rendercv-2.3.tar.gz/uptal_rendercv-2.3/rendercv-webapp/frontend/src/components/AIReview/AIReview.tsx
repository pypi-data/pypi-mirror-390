import React from "react";
import { IconArrowLeft, IconRefresh } from "@tabler/icons-react";
import { IconBulb, IconAlertCircle } from "@tabler/icons-react";
// @ts-ignore - react-apexcharts type issue
import ReactApexChart from "react-apexcharts";

const Chart = ReactApexChart as any;

interface AIReviewData {
  score: number;
  previousScore?: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: Array<{
    icon: "bulb" | "alert";
    title: string;
    description: string;
  }>;
  comparisonData: number[]; // Distribution data for histogram
}

interface AIReviewProps {
  onBack: () => void;
  onRefresh?: () => void;
  data?: AIReviewData;
}

const AIReview: React.FC<AIReviewProps> = ({
  onBack,
  onRefresh,
  data = {
    score: 80,
    previousScore: 65,
    summary:
      "The resume shows significant improvements in structure and clarity, making it more professional and easier to read. However, there are still minor errors and areas for further enhancement to achieve a polished final product.",
    strengths: [
      "Your resume highlights key skills relevant to the role.",
      "Clear structure makes it easy to scan.",
      "Some job titles and responsibilities are well-aligned with industry standards.",
      "Professional tone is consistent across most sections.",
    ],
    weaknesses: [
      "Missing measurable achievements (e.g., numbers, percentages, outcomes).",
      "Limited tailoring for this specific job role and keywords.",
      "Formatting inconsistencies may affect ATS readability.",
      "Some sections lack detail, making your expertise less impactful.",
    ],
    suggestions: [
      {
        icon: "bulb",
        title:
          "Education Dates Missing in license degree in Business Management at University of Hassiba Benbouali",
        description:
          "As a fresh graduate, adding dates can help recruiters understand your candidacy better.",
      },
      {
        icon: "alert",
        title:
          "Education Dates Missing in license degree in Business Management at University of Hassiba Benbouali",
        description:
          "As a fresh graduate, adding dates can help recruiters understand your candidacy better.",
      },
    ],
    comparisonData: [
      10, 15, 20, 25, 30, 35, 45, 50, 55, 60, 65, 70, 75, 80, 75, 70, 65, 60,
      50, 45, 40, 35, 30, 25, 20, 15, 10, 8, 5, 3,
    ],
  },
}) => {
  const score = data.score;
  const previousScore = data.previousScore;
  const improvement = previousScore ? score - previousScore : 0;

  // RadialBar chart configuration for score gauge
  const radialBarState = React.useMemo(
    () => ({
      series: [score],
      options: {
        chart: {
          type: "radialBar",
          offsetY: -20,
          sparkline: {
            enabled: true,
          },
        },
        plotOptions: {
          radialBar: {
            startAngle: -90,
            endAngle: 90,
            hollow: {
              margin: 0,
              size: "70%",
              background: "#fff",
              image: undefined,
              position: "front",
              dropShadow: {
                enabled: false,
              },
            },
            track: {
              background: "#e7e7e7",
              strokeWidth: "67%",
              margin: 0,
            },
            dataLabels: {
              show: true,
              name: {
                offsetY: -20,
                show: true,
                color: "#888",
                fontSize: "17px",
              },
              value: {
                formatter: function (val: number) {
                  return val + "%";
                },
                color: "#111",
                fontSize: "36px",
                show: true,
                offsetY: -16,
              },
            },
          },
        },
        fill: {
          type: "gradient",
          gradient: {
            shade: "light",
            type: "horizontal",
            shadeIntensity: 0.5,
            gradientToColors: ["#ABE5A1"],
            inverseColors: true,
            opacityFrom: 1,
            opacityTo: 1,
            stops: [0, 100],
          },
        },
        stroke: {
          lineCap: "round",
        },
        labels: ["Score"],
      },
    }),
    [score]
  );

  // Bar chart configuration for comparison
  const barChartState = React.useMemo(
    () => ({
      options: {
        chart: {
          id: "comparison-chart",
          type: "bar",
        },
        xaxis: {
          categories: [0, 30, 60, 90, 100],
        },
        plotOptions: {
          bar: {
            borderRadius: 4,
            distributed: false,
          },
        },
        dataLabels: {
          enabled: false,
        },
      },
      series: [
        {
          name: "Distribution",
          data: data.comparisonData
            .filter((_, idx) => idx % 6 === 0)
            .slice(0, 5),
        },
      ],
    }),
    [data.comparisonData]
  );

  return (
    <div className="h-full bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between sticky top-0 z-10">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-gray-700 hover:text-gray-900 transition-colors"
        >
          <IconArrowLeft size={20} />
          <span className="font-medium">Back</span>
        </button>
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="flex items-center gap-2 text-gray-700 hover:text-gray-900 transition-colors"
          >
            <IconRefresh size={20} />
            <span className="font-medium">Refresh</span>
          </button>
        )}
      </div>

      {/* Title */}
      <div className="bg-white px-6 py-4 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-900">AI Review</h1>
      </div>

      {/* Content */}
      <div className="bg-white flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {/* Resume Match Score Section */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            Resume Match Score
          </h2>

          <div className="flex flex-col lg:flex-row gap-8">
            {/* Left - Score Gauge (RadialBar) */}
            <div className="flex-1 flex flex-col items-center">
              {/* @ts-ignore */}
              <Chart
                options={radialBarState.options}
                series={radialBarState.series}
                type="radialBar"
                width={"100%"}
                height={200}
              />
              {improvement > 0 && (
                <div className="flex items-center gap-1 text-green-600 font-medium mt-2">
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 10l7-7m0 0l7 7m-7-7v18"
                    />
                  </svg>
                  <span>+{improvement}%</span>
                </div>
              )}
              {previousScore && (
                <div className="text-sm text-gray-500 mt-1">
                  from previous score of {previousScore}%
                </div>
              )}
            </div>

            {/* Right - Comparison Chart */}
            <div className="flex-1">
              {/* @ts-ignore */}
              <Chart
                options={barChartState.options}
                series={barChartState.series}
                type="bar"
                width="100%"
                height={200}
              />
            </div>
          </div>
        </div>

        {/* Summary Section */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Summary</h2>
          <p className="text-gray-700 leading-relaxed">{data.summary}</p>
        </div>

        {/* Strengths Section */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Strengths
          </h2>
          <ul className="space-y-3">
            {data.strengths.map((strength, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-gray-500 mt-2 flex-shrink-0" />
                <span className="text-gray-700">{strength}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Weaknesses Section */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Weaknesses
          </h2>
          <ul className="space-y-3">
            {data.weaknesses.map((weakness, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-gray-500 mt-2 flex-shrink-0" />
                <span className="text-gray-700">{weakness}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Boost Your Score Section */}
        <div className="bg-white rounded-lg p-5 shadow-sm  border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Boost Your Score
          </h2>
          <div className="">
            {data.suggestions.map((suggestion, idx) => (
              <div
                key={idx}
                className="   p-2 flex items-start gap-4 hover:border-gray-300 transition-colors"
              >
                <div className="flex-shrink-0 mt-1">
                  {suggestion.icon === "bulb" ? (
                    <IconBulb
                      size={24}
                      className="text-yellow-500"
                      style={{
                        filter: "drop-shadow(0 0 4px rgba(234, 179, 8, 0.5))",
                      }}
                    />
                  ) : (
                    <IconAlertCircle size={24} className="text-red-500" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-gray-900 font-medium mb-1">
                    {suggestion.title}
                  </p>
                  <p className="text-gray-600 text-sm">
                    {suggestion.description}
                  </p>
                </div>
                {/* <button className="flex-shrink-0 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium text-sm">
                  Resolve
                </button> */}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIReview;
