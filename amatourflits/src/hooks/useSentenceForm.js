// src/hooks/useSentenceForm.js
import { useState, useEffect } from 'react';

const useSentenceForm = (initialVoices) => {
    const [sentences, setSentences] = useState([]);

    useEffect(() => {
        if (initialVoices.length > 0 && sentences.length === 0) {
            const randomVoiceId = initialVoices[Math.floor(Math.random() * initialVoices.length)].voice_id;
            setSentences([{ text: '', voiceId: randomVoiceId }]);
        }
    }, [initialVoices, sentences.length]);

    const addSentence = () => {
        const randomVoiceId = initialVoices.length > 0 ? initialVoices[Math.floor(Math.random() * initialVoices.length)].voice_id : '';
        setSentences(currentSentences => [...currentSentences, { text: '', voiceId: randomVoiceId }]);
    };

    const removeSentence = (index) => {
        setSentences(currentSentences => currentSentences.filter((_, i) => i !== index));
    };

    const updateSentence = (index, key, value) => {
        setSentences(currentSentences => {
            const newSentences = [...currentSentences];
            newSentences[index][key] = value;
            return newSentences;
        });
    };

    return {
        sentences,
        setSentences,
        addSentence,
        removeSentence,
        updateSentence
    };
};

export default useSentenceForm;