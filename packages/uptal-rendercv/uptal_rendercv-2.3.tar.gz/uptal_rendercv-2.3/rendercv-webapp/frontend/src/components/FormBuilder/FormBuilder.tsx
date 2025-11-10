import React, { useState } from "react";
import { Accordion, AccordionSummary, AccordionDetails } from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
// import CheckIcon from "@mui/icons-material/Check";
import PersonalInfo from "./PersonalInfo";
import EducationForm from "./EducationForm";
import WorkExperienceForm from "./WorkExperienceForm";
import SkillsForm from "./SkillsForm";
import SummaryForm from "./SummaryForm";

const FormBuilder: React.FC = () => {
  const [expanded, setExpanded] = useState<string | false>("personal");

  const handleChange =
    (panel: string) => (_event: React.SyntheticEvent, isExpanded: boolean) => {
      setExpanded(isExpanded ? panel : false);
    };

  // Status configuration for each section
  const sections = [
    {
      id: "personal",
      title: "Personal Info",
      status: "error",
      errorCount: 1,
      component: <PersonalInfo />,
    },
    {
      id: "education",
      title: "Education",
      status: "complete",
      component: <EducationForm />,
    },
    {
      id: "work",
      title: "Work Experience",
      status: "error",
      errorCount: 2,
      component: <WorkExperienceForm />,
    },
    {
      id: "skills",
      title: "Skills",
      status: "complete",
      component: <SkillsForm />,
    },
    {
      id: "summary",
      title: "Summary",
      status: "complete",
      component: <SummaryForm />,
    },
  ];

  // const renderStatusIndicator = (section: (typeof sections)[0]) => {
  //   // if (section.status === "complete") {
  //   //   return (
  //   //     <div className="w-6 h-6 bg-green-200 rounded-full flex items-center justify-center shadow-sm  ">
  //   //       <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center shadow-sm  ">
  //   //         <CheckIcon
  //   //           className="text-white  flex items-center justify-center "
  //   //           style={{ fontSize: "12px" }}
  //   //         />
  //   //       </div>
  //   //     </div>
  //   //   );
  //   // } else if (section.status === "error") {
  //   //   return (
  //   //     <div className="w-6 h-6 bg-red-200 rounded-full flex items-center justify-center shadow-sm  ">
  //   //       <div className="w-4 h-4 bg-red-500 rounded-full flex items-center justify-center text-center shadow-sm  ">
  //   //         <span className="text-white  text-[10px] flex items-center justify-center  ">
  //   //           {section.errorCount}
  //   //         </span>
  //   //       </div>
  //   //     </div>
  //   //   );
  //   // }
  //   return null;
  // };

  return (
    <div className="bg-white  lg:bg-gray-100 p-4 min-h-screen">
      <div className="space-y-3">
        {sections.map((section) => (
          <Accordion
            key={section.id}
            expanded={expanded === section.id}
            onChange={handleChange(section.id)}
            className="bg-white rounded-lg shadow-sm border border-gray-200"
            sx={{
              "&:before": {
                display: "none",
              },
              boxShadow: "none",
              border: "1px solid #e5e7eb",
              borderRadius: "10px",
              marginBottom: "12px",
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon className="text-gray-600" />}
              className="px-4 py-3"
              sx={{
                minHeight: "56px",
                "& .MuiAccordionSummary-content": {
                  margin: "12px 0",
                  alignItems: "center",
                  justifyContent: "space-between",
                },
                "& .MuiAccordionSummary-expandIconWrapper": {
                  color: "#E2E8F0",
                },
                borderBottom: "2px solid #e5e7eb",
              }}
            >
              <div className="flex items-center justify-between w-full  ">
                <p className="text-gray-900 text-lg font-medium ">
                  {section.title}
                </p>
                {/* {renderStatusIndicator(section)} */}
              </div>
            </AccordionSummary>
            <AccordionDetails className="px-4 pb-4">
              {section.component}
            </AccordionDetails>
          </Accordion>
        ))}
      </div>
    </div>
  );
};

export default FormBuilder;
