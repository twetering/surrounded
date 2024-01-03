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
        setSentences([...sentences, { text: '', voiceId: randomVoiceId }]);
    };

    const removeSentence = (index) => {
        setSentences(sentences.filter((_, i) => i !== index));
    };

    const updateSentence = (index, key, value) => {
        const newSentences = [...sentences];
        newSentences[index][key] = value;
        setSentences(newSentences);
    };

    return {
        sentences,
        addSentence,
        removeSentence,
        updateSentence
    };
};

export default useSentenceForm;
