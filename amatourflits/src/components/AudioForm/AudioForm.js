import React from 'react';
import { Container, Paper, Typography, CircularProgress, Button } from '@mui/material';
import useVoices from '../../hooks/useVoices';
import useGenerateMultipleVoices from '../../hooks/useGenerateMultipleVoices';
import SentenceForm from '../SentenceForm/SentenceForm';
import useSentenceForm from '../../hooks/useSentenceForm';
import ReactPlayer from 'react-player';

function AudioForm() {
    const { voices } = useVoices();
    const { generateVoices, audioUrl, loading, error } = useGenerateMultipleVoices(); 
    const { sentences, addSentence, removeSentence, updateSentence } = useSentenceForm(voices);

    const handleSubmit = (event) => {
        event.preventDefault();
        generateVoices(sentences);
    };

    return (
        <Container component="main" maxWidth="lg">
            <Paper 
                style={{ padding: '20px', marginTop: '20px', backgroundColor: '#f5f5f5' }} 
                elevation={6}
            >
                <Typography 
                    variant="h4" 
                    className="roboto-slab" 
                    style={{ color: '#3f51b5', marginBottom: '20px' }}
                >
                    Meerdere Stemmen Genereren
                </Typography>
                <form onSubmit={handleSubmit}>
                    {sentences.map((sentence, index) => (
                        <SentenceForm
                            key={index}
                            index={index}
                            sentence={sentence}
                            voices={voices}
                            onSentenceChange={updateSentence}
                            onRemoveSentence={removeSentence}
                        />
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
                                    <CircularProgress 
                                        size={24} 
                                        style={{ marginRight: '10px' }} 
                                    />
                                    Genereren...
                                </>
                            ) : 'Genereer Stemmen'}
                        </Button>
                    </div>
                    {audioUrl && (
                        <div style={{ 
                            marginTop: '20px', 
                            display: 'flex', 
                            flexDirection: 'column', 
                            alignItems: 'center', 
                            justifyContent: 'center' 
                            }}
                        >
                            <Typography 
                                variant="h5" 
                                className="roboto-slab" 
                                style={{ color: '#3f51b5', marginBottom: '20px' }}
                            >
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
