import axios from "axios";
import { CVData, Theme } from "../types/cv.types";
import { JobAnalysis, ResumeAnswers } from "../types/jobAnalysis.types";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:5001/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
    // Authorization: `Bearer uApWzzzfgygAiaybL7wcYx92Qz2JLm5Vbkb0ZcCri9tB`,
  },
});

export const cvApi = {
  // Render CV to PDF
  renderCV: async (
    cvData: CVData
  ): Promise<{ pdf_id: string; pdf_url: string }> => {
    const response = await api.post("/render", cvData);
    return response.data;
  },

  // Get PDF by ID
  getPdfUrl: (pdfId: string): string => {
    return `${API_BASE_URL}/pdf/${pdfId}`;
  },

  // Download PDF
  downloadPdf: async (pdfId: string, filename?: string): Promise<void> => {
    try {
      const response = await api.get(`/pdf/${pdfId}`, {
        responseType: "blob",
      });

      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename || "cv.pdf";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      console.error("Failed to download PDF:", error);
      throw error;
    }
  },

  // Validate CV data
  validateCV: async (
    cvData: CVData
  ): Promise<{ valid: boolean; errors?: string[] }> => {
    const response = await api.post("/validate", cvData);
    return response.data;
  },

  // Get available themes
  getThemes: async (): Promise<Theme[]> => {
    const response = await api.get("/themes");
    return response.data;
  },

  // Get sample CV
  getSampleCV: async (): Promise<CVData> => {
    const response = await api.get("/sample");
    return response.data;
  },

  // Get sample CV by code
  getSampleCVByCode: async (cvCode: string): Promise<CVData> => {
    const response = await api.get(`/sample/${cvCode}`);
    return response.data;
  },

  // Export CV
  exportCV: async (
    cvData: CVData,
    format: "yaml" | "json" | "markdown"
  ): Promise<Blob | any> => {
    const response = await api.post(`/export/${format}`, cvData, {
      responseType: format === "json" ? "json" : "blob",
    });
    return response.data;
  },

  // Import CV from YAML
  importCV: async (file: File): Promise<CVData> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/import", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data.cv_data;
  },

  // Parse CV using GPT-4o-mini
  parseCV: async (
    file: File,
    jobAnalysis?: JobAnalysis | null,
    resumeAnswers?: ResumeAnswers
  ): Promise<{ success: boolean; cv_data?: CVData; error?: string }> => {
    const formData = new FormData();
    formData.append("file", file);
    if (jobAnalysis) {
      formData.append("job_analysis", JSON.stringify(jobAnalysis));
    }
    if (resumeAnswers && Object.keys(resumeAnswers).length > 0) {
      formData.append("resume_answers", JSON.stringify(resumeAnswers));
    }

    try {
      const response = await api.post("/parse-cv", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.data) {
        return error.response.data;
      }
      return { success: false, error: error.message || "Failed to parse CV" };
    }
  },

  // Update CV edits
  updateCVEdits: async (
    cvCode: string,
    cvData: CVData
  ): Promise<{
    status: string | boolean;
    data?: any;
    error?: string;
    message?: string;
    redirect_url?: string;
  }> => {
    try {
      console.log("Updating CV with code:", cvCode);
      console.log("CV Data:", cvData);

      const response = await api.post(`/cv-enhance/${cvCode}/edits`, cvData, {
        headers: {
          "Content-Type": "application/json",
        },
      });

      console.log("Response received:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("Update CV error:", error);
      console.error("Error response:", error.response?.data);
      if (error.response?.data) {
        // Return the error data from the backend
        return error.response.data;
      }
      return {
        status: "error",
        error: error.message || "Failed to update CV",
      };
    }
  },

  // Get CV info by code
  getCVInfo: async (cvCode: string): Promise<any> => {
    try {
      const response = await api.get(`/info/${cvCode}`);
      return response.data;
    } catch (error: any) {
      console.error("Get CV info error:", error);
      if (error.response?.data) {
        return error.response.data;
      }
      throw error;
    }
  },
};
