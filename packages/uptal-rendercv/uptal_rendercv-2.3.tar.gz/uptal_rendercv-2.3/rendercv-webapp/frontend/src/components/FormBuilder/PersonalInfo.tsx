import React from "react";
import { useCV } from "../../hooks/useCV";

const PersonalInfo: React.FC = () => {
  const { cvData, updatePersonalInfo } = useCV();
  const { cv } = cvData;

  const handleChange =
    (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value;

      if (field === "LinkedIn") {
        const existing = cv.social_networks || [];
        const hasLinkedin = existing.some((s) => s.network === "LinkedIn");
        const updated = hasLinkedin
          ? existing.map((s) =>
              s.network === "LinkedIn" ? { ...s, username: value } : s
            )
          : [...existing, { network: "LinkedIn", username: value }];
        updatePersonalInfo({ social_networks: updated as any });
        return;
      }

      updatePersonalInfo({ [field]: value } as any);
    };

  const formFields = [
    {
      id: "name",
      label: "Full name",
      placeholder: "Full name here...",
      value: cv.name || "",
      required: true,
    },
    {
      id: "email",
      label: "Email address",
      placeholder: "your.email@example.com",
      value: cv.email || "",
      type: "email",
    },
    {
      id: "phone",
      label: "Phone number",
      placeholder: "Phone number",
      value: cv.phone || "",
    },
    {
      id: "LinkedIn",
      label: "Linkedin URL",
      placeholder: "seddikmounir",
      value:
        cv.social_networks?.find((s) => s.network === "LinkedIn")?.username ||
        "",
    },
    {
      id: "website",
      label: "Personal website or relevant link",
      placeholder: "https://behance.net/seddikmounir",
      value: cv.website || "",
      type:"url"
    },
    {
      id: "location",
      label: "Location",
      placeholder: "Nablus, Palestine",
      value: cv.location || "",
    },
  ];

  return (
    <div className=" bg-white">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {formFields.map((field) => (
          <div key={field.id} className="space-y-1">
            <label
              htmlFor={field.id}
              className="block text-sm font-medium text-gray-700"
            >
              {field.label}
            </label>
            <input
              id={field.id}
              type={field.type || "text"}
              value={field.value}
              onChange={handleChange(field.id)}
              placeholder={field.placeholder}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default PersonalInfo;
