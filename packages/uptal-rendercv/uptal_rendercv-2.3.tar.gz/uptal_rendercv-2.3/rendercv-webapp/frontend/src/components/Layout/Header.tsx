import React, { useState } from "react";
import { AppBar, Toolbar, Typography, Button, IconButton } from "@mui/material";
import toast from "react-hot-toast";
import { IconArrowLeft, IconDeviceFloppy } from "@tabler/icons-react";
import { useCV } from "../../hooks/useCV";
import { cvApi } from "../../services/api";
import { prepareCVData } from "../../utils/cvHelpers";
import { IconPalette } from "@tabler/icons-react";
import TemplateGallery from "../PdfViewer/TemplateGallery";

const Header: React.FC = () => {
  const { cvData, cvCode, startStatusPolling, showAIReview, isPollingStatus } =
    useCV();
  const [templateGalleryOpen, setTemplateGalleryOpen] = useState(false);

  const handleDownloadPDF = async () => {
    try {
      // Prepare CV data using the helper function
      const dataToSend = prepareCVData(cvData);
      console.log(dataToSend, "dataToSend");

      // Generate PDF
      toast.loading("Generating PDF...", { id: "pdf-download" });
      const response = await cvApi.renderCV(dataToSend);

      // Download the PDF
      const pdfFilename = `${cvData.cv.name || "cv"}_resume.pdf`;
      await cvApi.downloadPdf(response.pdf_id, pdfFilename);

      toast.success("PDF downloaded successfully!", { id: "pdf-download" });
    } catch (error: any) {
      console.error("PDF download error:", error);
      toast.error(error.response?.data?.error || "Failed to download PDF", {
        id: "pdf-download",
      });
    }
  };

  const handleSaveAndContinue = async () => {
    try {
      // Show loading toast
      toast.loading("Saving CV...", { id: "save-cv" });

      // Prepare CV data using the helper function
      const dataToSend = prepareCVData(cvData);

      // Send CV data as JSON to update CV edits
      console.log("Saving CV data to cvCode:", cvCode);
      const saveResponse = await cvApi.updateCVEdits(cvCode, dataToSend);

      console.log("Save response:", saveResponse);
      toast.success("CV saved successfully!", { id: "save-cv" });

      if (saveResponse.status === "success" || saveResponse.status === true) {
        startStatusPolling(cvCode);
      } else {
        const errorMsg =
          saveResponse.error ||
          saveResponse.message ||
          "Failed to save CV. Please try again.";
        toast.error(errorMsg, {
          id: "save-cv",
        });
      }
    } catch (error: any) {
      console.error("Save CV error:", error);
      const errorMsg =
        error.response?.data?.error ||
        error.response?.data?.message ||
        error.message ||
        "Failed to save CV. Please try again.";
      toast.error(errorMsg, {
        id: "save-cv",
      });
    }
  };

  const handleBackToApplication = () => {
    // Add navigation logic here
    window.history.back();
  };

  const handleContinue = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const redirectUrl = urlParams.get("redirectUrl");
    if (redirectUrl) {
      window.location.href = redirectUrl;
    } else {
      // Fallback to going back if no redirect URL
      window.history.back();
    }
  };

  return (
    <AppBar
      position="static"
      sx={{
        backgroundColor: "#fff",
        boxShadow: "none",
        borderBottom: "1px solid #e0e0e0",
      }}
    >
      <Toolbar className="justify-between min-h-16 px-4 sm:px-6">
        {/* Left side - Back to Application */}
        <div className="flex items-center">
          <IconButton
            onClick={handleBackToApplication}
            className="text-black hover:bg-gray-100 transition-colors duration-200"
            size="small"
          >
            <IconArrowLeft color="#000000" size={20} />
          </IconButton>
          <Typography className="text-black text-sm hidden sm:block">
            Back to Application
          </Typography>
        </div>

        {/* Center - CV Title with edit icon */}
        <div className="flex items-center space-x-2 flex-1 justify-center"></div>

        {/* Right side - Buttons */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Desktop only buttons */}
          <div className="hidden sm:flex items-center space-x-3">
            {/* Select Template - hide when analysis is complete */}
            {!showAIReview && !isPollingStatus && (
              <Button
                variant="outlined"
                startIcon={<IconPalette />}
                onClick={() => setTemplateGalleryOpen(true)}
                sx={{
                  textTransform: "none",
                  borderColor: "#E5E7EBB8",
                  color: "#11181C",
                }}
              >
                Select Template
              </Button>
            )}

            {/* Download PDF - always visible on desktop */}
            {!isPollingStatus && (
              <Button
                variant="outlined"
                startIcon={<IconDeviceFloppy />}
                onClick={handleDownloadPDF}
                sx={{
                  textTransform: "none",
                  borderColor: "#E5E7EBB8",
                  color: "#11181C",
                }}
              >
                Download PDF
              </Button>
            )}
          </div>

          {/* Analyze button - visible when analysis is not complete */}
          {!showAIReview && !isPollingStatus && (
            <Button
              variant="contained"
              onClick={handleSaveAndContinue}
              className="bg-blue-600 hover:bg-blue-700 text-white normal-case transition-colors duration-200"
              sx={{
                textTransform: "none",
              }}
            >
              Analyze
            </Button>
          )}

          {/* Continue button - visible when analysis is complete and redirectUrl exists */}
          {showAIReview && !isPollingStatus && (
            <Button
              variant="contained"
              onClick={handleContinue}
              className="bg-green-600 hover:bg-green-700 text-white normal-case transition-colors duration-200"
              sx={{
                textTransform: "none",
              }}
            >
              Continue
            </Button>
          )}
        </div>
      </Toolbar>
      {/* Template Gallery Drawer */}
      <TemplateGallery
        open={templateGalleryOpen}
        onClose={() => setTemplateGalleryOpen(false)}
      />
    </AppBar>
  );
};

export default Header;
