import { NextApiRequest, NextApiResponse } from 'next';
import OpenAI from 'openai';
import fs from 'fs';
import path from 'path';

const pdfParse = require('pdf-parse');

// Initialize OpenAI API
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// Store combined text
let combinedText = '';

// Function to load and combine text from PDFs
async function loadPDFs() {
    try {
        const pdfPaths = [
            path.join(process.cwd(), 'public', 'budget.pdf'),
            path.join(process.cwd(), 'public', 'transcript.pdf'),
        ];

        let allText = '';
        for (const pdfPath of pdfPaths) {
            console.log(`Reading PDF: ${pdfPath}`);
            const dataBuffer = fs.readFileSync(pdfPath);
            const data = await pdfParse(dataBuffer);
            console.log(`Extracted Text Length from ${pdfPath}: ${data.text.length}`);
            allText += data.text + '\n\n';
        }

        combinedText = allText;
        console.log('Combined Text Loaded. Length:', combinedText.length);
    } catch (error) {
        console.error('Error loading PDFs:', error.message);
        throw new Error('Failed to load PDFs');
    }
}

// Load PDFs when the server starts
loadPDFs();

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    console.log('API /api/query called');
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method Not Allowed' });
    }

    const { query } = req.body;

    if (!query) {
        console.log('No query provided');
        return res.status(400).json({ error: 'No query provided' });
    }

    if (!combinedText) {
        console.error('Combined text not loaded');
        return res.status(500).json({ error: 'PDF content is not loaded yet.' });
    }

    try {
        const response = await openai.chat.completions.create({
            model: "gpt-4",
            messages: [
                { role: "system", content: "You are a helpful assistant for India's 2025 budget and related announcements." },
                { role: "user", content: `Based on these documents, answer this query: ${query}\n\n${combinedText}` },
            ],
            max_tokens: 500,
            temperature: 0.7,
        });

        console.log('OpenAI API Response:', response);
        const answer = response.choices?.[0]?.message?.content || 'No response received from OpenAI.';
        res.status(200).json({ answer });
    } catch (error) {
        console.error('Error with OpenAI API:', error.response?.data || error.message);
        res.status(500).json({ error: 'An error occurred while processing your query.' });
    }
}