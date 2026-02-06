import { GoogleGenAI } from "@google/genai";

// Note: In a real app, use process.env.API_KEY.
// For this demo, we assume the environment is set up correctly.
const apiKey = process.env.API_KEY || '';

const ai = new GoogleGenAI({ apiKey });

export const analyzeNetwork = async (
  scenario: string, 
  studentCount: number, 
  teacherCount: number, 
  avgAccuracy: number
): Promise<string> => {
  if (!apiKey) {
    return "API Key not configured. Using simulated analysis: The current network shows strong clustering around core knowledge points. Teacher centrality is optimal for this class size.";
  }

  try {
    const prompt = `
      As an educational data analyst, provide a brief (max 60 words) insight for a class interactive network visualization.
      Context:
      - Scenario: ${scenario}
      - Students: ${studentCount}
      - Teachers: ${teacherCount}
      - Avg Resource Acceptance: ${avgAccuracy}%
      
      Analyze the potential engagement level and suggest one teaching intervention.
    `;

    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: prompt,
    });

    return response.text || "No analysis available.";
  } catch (error) {
    console.error("Gemini API Error:", error);
    return "Unable to generate AI analysis at this time. Network topology suggests balanced interaction.";
  }
};