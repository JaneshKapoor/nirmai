import { NextApiRequest, NextApiResponse } from 'next';
import OpenAI from 'openai';
import fs from 'fs';
// import pdfParse from 'pdf-parse';
import path from 'path';

const pdfParse = require('pdf-parse');

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
let combinedText = '';

// Function to load and combine text from multiple PDFs
async function loadPDFs() {
    const pdfPaths = [
        path.join(process.cwd(), 'public', 'budget.pdf'),
        path.join(process.cwd(), 'public', 'transcript.pdf'),
    ];

    let allText = '';
    for (const pdfPath of pdfPaths) {
        const dataBuffer = fs.readFileSync(pdfPath);
        const data = await pdfParse(dataBuffer);
        allText += data.text + '\n\n';
    }

    combinedText = allText;
}

// Load PDFs when the server starts
loadPDFs();

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method Not Allowed' });
    }

    const { query } = req.body;

    if (!query) {
        return res.status(400).json({ error: 'No query provided' });
    }

    try {
        const response = await openai.chat.completions.create({
            model: "gpt-4",
            messages: [
                { role: "system", content: "You are a helpful assistant for India's 2025 budget and related announcements." },
                { role: "user", content: `Based on these documents, answer this query: ${query}\n\n${combinedText}` }
            ],
            max_tokens: 500,
            temperature: 0.7,
        });

        res.status(200).json({ answer: response.choices[0].message.content });
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Something went wrong!' });
    }
}