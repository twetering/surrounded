// src/hooks/useVoices.js
import { useState, useEffect } from 'react';

const useVoices = () => {
    const [voices, setVoices] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchVoices = async () => {
            try {
                const response = await fetch('http://127.0.0.1:5000/get_voices');
                if (!response.ok) {
                    throw new Error(`HTTP status ${response.status}`);
                }
                console.log("Response received:", response); // Log de volledige response
                const voicesData = await response.json();
                setVoices(voicesData);
            } catch (error) {
                console.error('Error fetching voices:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchVoices();
    }, []);

    return { voices, loading };
};

export default useVoices;
