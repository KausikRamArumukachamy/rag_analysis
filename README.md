Here’s a **README.md** file for your project, documenting the **UploadPage.js** functionality and usage. Let me know if you need any modifications!  

---

## **README.md**

# **Document Upload & Processing Web App**

This project provides a React-based frontend for uploading **PDF** files. It allows users to **drag & drop** or **click to select** a file, which is then sent to a backend server for processing.

---

## **Features**
- 📂 **File Upload**: Users can upload PDFs files.  
- 🖱️ **Drag & Drop Support**: Easily add files by dragging them into the upload area.  
- 🔍 **File Validation**: Ensures that only PDF files are uploaded.  
- ⏳ **Loading Indicator**: Displays a loading animation while the file is being uploaded.  
- ❌ **Remove File Option**: Users can remove a selected file before uploading.  
- 🔄 **Error Handling**: Alerts users if there is an issue with the upload process.  
- 📡 **Backend Communication**: Sends the file to a backend server for processing.

---

## **Technologies Used**
- **React.js**  
- **CSS (for styling)**  
- **React Router** (for navigation)  
- **Fetch API** (for backend communication)  

---

## **Installation & Setup**

1. **Clone the repository**  
   ```sh
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. **Install dependencies**  
   ```sh
   npm install
   ```

3. **Run the application**  
   ```sh
   npm start
   ```

---

## **File Structure**
```
/src
 ├── assets/                # Stores images (upload icon, loading GIF, background)
 ├── pages/
 │   ├── UploadPage.js      # Main file upload component
 │   ├── UploadPage.css     # Styles for the upload page
 │   ├── AnalysisPage.js    # Main file analysis component
 │   ├── AnalysisPage.css   # Main file upload component
 ├── App.js                 # Main application file
 ├── index.js               # Entry point of the React app
```

---

## **Backend API**
The file is sent to the backend server at:  
**`https://rag-analysis.onrender.com/upload/`**  

- **Method**: `POST`  
- **Payload**:  
  ```sh
  FormData { file: selectedFile }
  ```
- **Response Handling**:  
  - ✅ **Success** → Navigates to `/analysis`  
  - ❌ **Failure** → Shows an alert with an error message  

---

## **How It Works**
1. The user selects or drags a **PDF** file.  
2. The file gets validated (only PDFs allowed).  
3. On clicking **Upload**, the file is sent to the backend.  
4. A loading spinner appears while the file is being processed.  
5. On success, the user is redirected to the **analysis page**.  
6. On failure, an error message is displayed.

---

## **Contributors**
- **Your Name** - *KausikRam Arumukachamy*  

---

Let me know if you want any modifications! 🚀