import React, { useState } from 'react';
import { TextField, Button, Container, Paper, Typography, Select, CircularProgress, MenuItem, FormControl, InputLabel } from '@mui/material';
import useVoices from '../../hooks/useVoices';
import useGenerateMultipleVoices from '../../hooks/useGenerateMultipleVoices';
import DeleteIcon from '@mui/icons-material/Delete';
import ReactPlayer from 'react-player';

function AudioForm() {
    const { voices } = useVoices();
    const { generateVoices, audioUrl, loading, error } = useGenerateMultipleVoices();  // Correct gebruik van de hook
    const [sentences, setSentences] = useState([{ text: '', voiceId: '' }]);

    const handleSentenceChange = (index, key, value) => {
        const newSentences = [...sentences];
        newSentences[index][key] = value;
        setSentences(newSentences);
    };

    const addSentence = () => {
        const randomVoiceId = voices.length > 0 ? voices[Math.floor(Math.random() * voices.length)].voice_id : '';
        setSentences([...sentences, { text: '', voiceId: randomVoiceId }]);
    };

    const removeSentence = (index) => {
        setSentences(sentences.filter((_, i) => i !== index));
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        generateVoices(sentences);  // Aangepast om de hook functie te gebruiken
    };

    return (
        <Container component="main" maxWidth="lg">
    <Paper style={{ padding: '20px', marginTop: '20px', backgroundColor: '#f5f5f5' }} elevation={6}>
        <Typography variant="h4" className="roboto-slab" style={{ color: '#3f51b5', marginBottom: '20px' }}>
            Meerdere Stemmen Genereren
        </Typography>
        <form onSubmit={handleSubmit}>
            {sentences.map((sentence, index) => (
            <div key={index} style={{ display: 'flex', alignItems: 'center', marginBottom: '15px' }}>
                <TextField
                    label={`Zin ${index + 1}`}
                    multiline
                    rows={2}
                    style={{ marginRight: '10px', flexGrow: 1 }}
                    variant="outlined"
                    value={sentence.text}
                    onChange={(e) => handleSentenceChange(index, 'text', e.target.value)}
                />
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <FormControl style={{ width: '200px', marginRight: '10px' }}>
                    <InputLabel id={`voice-select-label-${index}`}>Stem</InputLabel>
                    <Select
                        labelId={`voice-select-label-${index}`}
                        id={`voice-select-${index}`}
                        value={sentence.voiceId}
                        label="Stem"
                        onChange={(e) => handleSentenceChange(index, 'voiceId', e.target.value)}
                    >
                        {voices.map((voice) => (
                        <MenuItem key={voice.voice_id} value={voice.voice_id}>
                            {voice.name}
                        </MenuItem>
                        ))}
                    </Select>
                    </FormControl>
                    <Button 
                    variant="outlined" 
                    color="secondary"
                    onClick={() => removeSentence(index)}
                    >
                    <DeleteIcon />
                    </Button>
                </div>
            </div>
            ))}
            <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    width: '100%', 
                    marginBottom: '20px' 
                    }}>
                <Button 
                    variant="contained" 
                    color="secondary" 
                    onClick={addSentence} 
                    style={{ marginRight: '10px' }}
                >
                    Voeg Zin Toe
                </Button>
                <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    disabled={loading}
                >
                    {loading ? (
                        <>
                            <CircularProgress size={24} style={{ marginRight: '10px' }} />
                            Genereren...
                        </>
                    ) : 'Genereer Stemmen'}
                </Button>
            </div>
            {audioUrl && (
                <div style={{ marginTop: '20px', display: 'flex', flexDirection: 'column', alignItems: 'center',justifyContent: 'center' }}>
                    <Typography variant="h5" className="roboto-slab" style={{ color: '#3f51b5', marginBottom: '20px' }}>
                        Gegenereerde audio
                    </Typography>
                    <ReactPlayer
                        url={audioUrl}
                        controls={true}
                        width='50%'
                        height='50px'
                        style={{ borderRadius: '4px' }}
                        />
                </div>
            )}
            {error && <div>Error: {error}</div>}
        </form>
    </Paper>
</Container>
    );
}

export default AudioForm;
