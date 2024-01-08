import React from 'react';
import {useState} from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { Box, TextField, Button, Container, Paper, Typography, CircularProgress } from '@mui/material';
import useVoices from '../../hooks/useVoices';
import useGenerateMultipleVoices from '../../hooks/useGenerateMultipleVoices';
import SentenceForm from '../SentenceForm/SentenceForm';
import useSentenceForm from '../../hooks/useSentenceForm';
import AudioSettingsForm from '../AudioSettingsForm/AudioSettingsForm';
import ReactPlayer from 'react-player';
import DragHandleIcon from '@mui/icons-material/DragHandle';


function AudioForm() {
    const { voices } = useVoices();
    const { generateVoices, audioUrl, loading, error } = useGenerateMultipleVoices(); 
    const { sentences, setSentences, addSentence, removeSentence, updateSentence } = useSentenceForm(voices);
    
    const [audiosettings, setAudioSettings] = useState({
        intro: '',
        outro: '',
        bgaudio: ''
    });

    // Functie om de volgorde van zinnen aan te passen na het verslepen
    const onDragEnd = (result) => {
        if (!result.destination) {
            return;
        }

        const items = Array.from(sentences);
        const [reorderedItem] = items.splice(result.source.index, 1);
        items.splice(result.destination.index, 0, reorderedItem);

        // Update de volgorde van zinnen
        setSentences(items);
    };

    const handleSettingChange = (setting, value) => {
        setAudioSettings(prevSettings => ({
            ...prevSettings,
            [setting]: value
        }));
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        generateVoices(sentences, audiosettings);
    };

    return (
        <Container className="container">
            <Paper className="paper">
                <box className="typographyHeader">
                    <Typography 
                        variant="h4" 
                    >
                            Ontwerp je eigen Amatourflits
                    </Typography>
                </box>

                <form onSubmit={handleSubmit}>
                
                <TextField
                    id="test-field"
                    label="Testveld voor knippen en plakken"
                    multiline
                    rows={2}
                    className="testField"
                    variant="outlined"
                />
                
                    <AudioSettingsForm 
                        audiosettings={audiosettings} 
                        setAudioSettings={setAudioSettings} 
                        handleSettingChange={handleSettingChange}
                    />

                    <box className="typographyHeader">
                        <Typography variant="h5" className="typographyHeader">
                            Voeg fragmenten toe
                        </Typography>
                    </box>

                    <DragDropContext onDragEnd={onDragEnd}>
                        <Droppable droppableId="dropsentences">
                            {(provided) => (
                                <div 
                                    {...provided.droppableProps} 
                                    ref={provided.innerRef}
                                >
                                    {sentences.map((sentence, index) => (
                                        <Draggable 
                                            key={`sentence-${index}`} 
                                            draggableId={`sentence-${index}`} 
                                            index={index}
                                        >
                                            {(provided, snapshot) => (
                                                <div
                                                    ref={provided.innerRef}
                                                    {...provided.draggableProps}
                                                    className="draggableContainer"
                                                >
                                                    <div {...provided.dragHandleProps} 
                                                        className="dragHandleContainer">
                                                        <DragHandleIcon />
                                                    </div>
                                                   
                                                    <SentenceForm
                                                        index={index}
                                                        sentence={sentence}
                                                        voices={voices}
                                                        onSentenceChange={updateSentence}
                                                        onRemoveSentence={removeSentence}
                                                    />
                                                </div>
                                            )}
                                        </Draggable>
                                    ))}
                                    {provided.placeholder}
                                </div>
                            )}
                        </Droppable>
                    </DragDropContext>

                    <div className="buttonGroup">
                        <Button 
                            variant="contained" 
                            color="secondary" 
                            onClick={addSentence} 
                            className="addButton"
                        >
                            Voeg Fragment Toe
                        </Button>
                        <Box mr={2} />
                        <Button
                            type="submit"
                            variant="contained"
                            color="primary"
                            disabled={loading}
                            className="submitButton"
                        >
                            {loading ? (
                                <>
                                    <CircularProgress 
                                        size={24} 
                                        className="addRemoveButton"
                                    />
                                    Genereren...
                                </>
                            ) : 'Genereer Stemmen'}
                        </Button>
                    </div>
                    {audioUrl && (
                        <div className="audioSection">
                            <box className="typographyHeader">
                                <Typography 
                                    variant="h5" 
                                >
                                    Luister of download je Amatourflits
                                </Typography>
                            </box>
                                <ReactPlayer
                                    url={audioUrl}
                                    controls={true}
                                    className="audioPlayer"
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
