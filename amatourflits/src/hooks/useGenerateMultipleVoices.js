// src/hooks/useGenerateMultipleVoices.js
import { useState } from 'react';

const useGenerateMultipleVoices = () => {
    const [audioUrl, setAudioUrl] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const generateVoices = async (textVoicePairs, audioSettings) => {
        setLoading(true);
        setError(null);
        try {
            const introPath = audioSettings.intro ? `amatourflits/intros/${audioSettings.intro}` : '';
            const outroPath = audioSettings.outro ? `amatourflits/outros/${audioSettings.outro}` : '';
            const bgAudioPath = audioSettings.bgaudio ? `amatourflits/bgaudio/${audioSettings.bgaudio}` : '';

            const response = await fetch('http://127.0.0.1:5000/generate-multiple-voices', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ textVoicePairs, intro: introPath, outro: outroPath, bgaudio: bgAudioPath }),
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setAudioUrl(data.audio_file);
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    return { generateVoices, audioUrl, loading, error };
};

export default useGenerateMultipleVoices;
