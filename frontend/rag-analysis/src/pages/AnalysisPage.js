import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie } from "recharts";
import ReactMarkdown from "react-markdown";
import "./AnalysisPage.css";
import loadingGIF from "../assets/cheems_loading.gif"
import loadGIF from "../assets/loading.webp"


const AnalysisPage = () => {
    const [chatSessions, setChatSessions] = useState([]);
    const [activeChatIndex, setActiveChatIndex] = useState(null);
    const [input, setInput] = useState("");
    const [isHovered, setIsHovered] = useState(false);
    const chatHistoryRef = useRef(null);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    
    useEffect(() => {
        const storedChats = localStorage.getItem("chatSessions");
        const storedActiveIndex = localStorage.getItem("activeChatIndex");
    
        if (storedChats) {
            setChatSessions(JSON.parse(storedChats));
        }
    
        if (storedActiveIndex !== null) {
            setActiveChatIndex(JSON.parse(storedActiveIndex));
        } else if (storedChats) {
            setActiveChatIndex(0); 
        }
    
        // ✅ Automatically create a new chat session if none exist
        if (!storedChats || JSON.parse(storedChats).length === 0) {
            const initialChat = [{ title: "Chat 1", messages: [] }];
            setChatSessions(initialChat);
            setActiveChatIndex(0);
            localStorage.setItem("chatSessions", JSON.stringify(initialChat));
            localStorage.setItem("activeChatIndex", JSON.stringify(0));
        }
    }, []);
    
    useEffect(() => {
        if (chatSessions.length > 0) {
            localStorage.setItem("chatSessions", JSON.stringify(chatSessions));
        }
    }, [chatSessions]);
    
    // Save activeChatIndex when it changes
    useEffect(() => {
        if (activeChatIndex !== null) {
            localStorage.setItem("activeChatIndex", JSON.stringify(activeChatIndex));
        }
    }, [activeChatIndex]);
    

    const handleSend = async () => {
        if (input.trim() === "") return;
    
        setChatSessions((prevChats) => {
            let updatedChats = [...prevChats];
    
            if (prevChats.length === 0) {
                updatedChats = [{ title: "Chat 1", messages: [] }];
                setActiveChatIndex(0);
            }
    
            const newUserMessage = { type: "user", text: input };
    
            const chatIndex = activeChatIndex !== null ? activeChatIndex : 0;
            if (updatedChats[chatIndex]) {
                updatedChats = updatedChats.map((chat, index) =>
                    index === chatIndex
                        ? { ...chat, messages: [...chat.messages, newUserMessage] }
                        : chat
                );
            }
    
            return updatedChats;
        });
    
        setInput("");
    
        // Add loading message
        const loadingMessage = { type: "loading" };
    
        setChatSessions((prevChats) => {
            let updatedChats = [...prevChats];
            const chatIndex = activeChatIndex !== null ? activeChatIndex : 0;
    
            if (updatedChats[chatIndex]) {
                updatedChats = updatedChats.map((chat, index) =>
                    index === chatIndex
                        ? { ...chat, messages: [...chat.messages, loadingMessage] }
                        : chat
                );
            }
    
            return updatedChats;
        });

        const BACKEND_URL = "https://rag-analysis.onrender.com";
    
        try {
            const response = await axios.get(`${BACKEND_URL}/query/`, {
                params: { user_query: input },
            });
    
            const chatIndex = activeChatIndex !== null ? activeChatIndex : 0;
    
            const systemResponse = response.data.ai_response.chartNeeded
                ? {
                      type: "system",
                      text: response.data.ai_response.text,
                      chartType: response.data.ai_response.chart.type,
                      chartLabels: response.data.ai_response.chart.data.labels,
                      chartValues: response.data.ai_response.chart.data.values,
                  }
                : { type: "system", text: response.data.ai_response.text };
    
            setChatSessions((prevChats) => {
                let updatedChats = [...prevChats];
    
                if (updatedChats[chatIndex]) {
                    updatedChats = updatedChats.map((chat, index) =>
                        index === chatIndex
                            ? {
                                  ...chat,
                                  messages: chat.messages.map((msg) =>
                                      msg.type === "loading" ? systemResponse : msg
                                  ),
                              }
                            : chat
                    );
                }
    
                return updatedChats;
            });
        } catch (error) {
            console.error("Error fetching AI response:", error);
            const errorMessage = { type: "system", text: "Error fetching response. Try again." };
    
            setChatSessions((prevChats) => {
                let updatedChats = [...prevChats];
                const chatIndex = activeChatIndex !== null ? activeChatIndex : 0;
                if (updatedChats[chatIndex]) {
                    updatedChats = updatedChats.map((chat, index) =>
                        index === chatIndex
                            ? {
                                  ...chat,
                                  messages: chat.messages.map((msg) =>
                                      msg.type === "loading" ? errorMessage : msg
                                  ),
                              }
                            : chat
                    );
                }
                return updatedChats;
            });
        }
    };        

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleNewChat = () => {
        const newChat = { title: `Chat ${chatSessions.length + 1}`, messages: [] };
        const updatedChats = [...chatSessions, newChat];
        setChatSessions(updatedChats);
        setActiveChatIndex(chatSessions.length);
        localStorage.setItem("chatSessions", JSON.stringify(updatedChats));
    };

    const validateFileType = (file) => {
        const allowedExtensions = [".pdf", ".docx"];
        return allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    };

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (!file) return;
    
        if (validateFileType(file)) {
            setSelectedFile(file); 
            setTimeout(() => handleUploadFile(file), 0);
        } else {
            alert("Only PDF and Word documents are allowed!");
        }
    };

    const handleUploadFile = async (file) => {
        if (!file) return;
        console.log("Attempting to upload:", file.name);
    
        const formData = new FormData();
        formData.append("file", file);
    
        setIsLoading(true);

        const BACKEND_URL = "https://rag-analysis.onrender.com";
    
        try {
            const response = await fetch(`${BACKEND_URL}/upload/`, {
                method: "POST",
                body: formData,
            });
    
            const data = await response.json();
            console.log("Upload response:", data);
    
            if (response.ok) {
                alert(`Upload Successful: ${data.message}`);
            } else {
                alert(`Upload Failed: ${data.detail || "Unknown error"}`);
            }
        } catch (error) {
            console.error("Upload error:", error);
            alert("Failed to upload the file. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };
    
    const handleChatSelect = (index) => {
        if (index !== activeChatIndex) {
            setActiveChatIndex(index);
            localStorage.setItem("activeChatIndex", JSON.stringify(index));
        }
    };
       

    const handleDeleteChat = (index) => {
        const updatedChats = chatSessions.filter((_, i) => i !== index);
        setChatSessions(updatedChats);
        setActiveChatIndex(updatedChats.length > 0 ? 0 : null);
        localStorage.setItem("chatSessions", JSON.stringify(updatedChats));
    };

    useEffect(() => {
        if (chatHistoryRef.current && chatSessions.length > 1) {
            chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
        }
    }, [chatSessions]);

    return (
        <div className="analysis-container">
            <div className="sidebar">
                <h3>Chats</h3>
                <button
                    className="new-chat-button"
                    onClick={handleNewChat}
                    onMouseEnter={() => setIsHovered(true)}
                    onMouseLeave={() => setIsHovered(false)}
                >
                    {isHovered ? "New Chat" : "+"}
                </button>

                <button
                    className="upload-button"
                    onMouseEnter={() => setIsHovered(true)}
                    onMouseLeave={() => setIsHovered(false)}
                    onClick={() => document.getElementById("fileInput").click()}
                    
                >
                    {isHovered ? "Upload File" : "📂"}
                    <input 
                        type="file"
                        id="fileInput"
                        onChange={handleFileChange}
                        accept=".pdf, .docx"
                        style={{ display: "none" }} />
                </button>
                <div className="chat-history" ref={chatHistoryRef}>
                    {chatSessions.map((chat, index) => (
                        <div key={index} 
                            className={`chat-item ${activeChatIndex === index ? "active-chat" : ""}`} 
                            onClick={() => handleChatSelect(index)}>
                            <span onClick={() => handleChatSelect(index)}>{chat.title}</span>
                            <button className="delete-chat-button" onClick={() => handleDeleteChat(index)}>✖</button>
                        </div>
                    ))}
                </div>
            </div>

            <div className="chat-area">
                <div className="chat-box">
                    {activeChatIndex !== null &&
                        chatSessions[activeChatIndex]?.messages.map((message, index) => (
                            <div key={index} className={message.type === "user" ? "user-message" : "system-message"}>
                                {/* Always render the text */}
                                {message.type === "loading" ? (
                                    <img src={loadGIF} alt="Loading..." className="loading-gif" />
                                ) : (
                                    <ReactMarkdown>{message.text}</ReactMarkdown>
                                )}
                                
                                {message.type === "system" &&
                                    message.chartLabels &&
                                    message.chartValues &&
                                    message.chartLabels.length > 0 &&
                                    message.chartValues.length > 0 && (
                                        <div className="chart-container">
                                            {message.chartType.toLowerCase() === "bar" && (
                                                <ResponsiveContainer width="100%" height={300}>
                                                    <BarChart
                                                        data={message.chartLabels.map((label, i) => ({
                                                            name: label,
                                                            value: message.chartValues[i],
                                                        }))}
                                                    >
                                                        <XAxis dataKey="name" />
                                                        <YAxis />
                                                        <Tooltip />
                                                        <Bar dataKey="value" fill="#8884d8" />
                                                    </BarChart>
                                                </ResponsiveContainer>
                                            )}

                                            {message.chartType.toLowerCase() === "pie" && (
                                                <ResponsiveContainer width="100%" height={300}>
                                                    <PieChart>
                                                        <Pie
                                                            data={message.chartLabels.map((label, i) => ({
                                                                name: label,
                                                                value: message.chartValues[i],
                                                            }))}
                                                            dataKey="value"
                                                            nameKey="name"
                                                            fill="#82ca9d"
                                                            label
                                                        />
                                                    </PieChart>
                                                </ResponsiveContainer>
                                            )}
                                        </div>
                                    )}

                            </div>
                        ))}
                </div>

                <div className="input-container">
                    <textarea
                        className="input-box"
                        placeholder="Type your message here"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={chatSessions.length === 0 && activeChatIndex !== null}
                    ></textarea>
                    <button className="send-button" onClick={handleSend}>
                        ➝
                    </button>
                </div>
            </div>

            {isLoading && (
                <div className="loading-overlay">
                    <img src={loadingGIF} alt="Loading..." className="loading-spinner" />
                    <p>Processing File, Please Wait...</p>
                </div>
            )}
        </div>
    );
};

export default AnalysisPage;
