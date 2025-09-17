# Mega Project 🚀

This repository contains multiple AI/ML projects developed for research and practical applications in healthcare and conversational systems.

---

## 📌 Projects

### 1. Advance_Chatbot
**Description:**  
An advanced chatbot designed to provide human-like interaction.  
- Uses **NLP (Natural Language Processing)** techniques.  
- Can handle **multi-turn conversations**.  
- Useful for customer support and educational assistance.

**Features:**  
- Context-aware replies  
- Integration with APIs  
- Scalable for different domains  

---

### 2. MRI_3D
**Description:**  
A deep learning model for **3D MRI Tumor Detection**.  
- Helps in detecting brain tumors from MRI scans.  
- Uses **Convolutional Neural Networks (CNNs)** for classification.  

**Features:**  
- Early diagnosis support  
- 3D medical image analysis  
- Can be extended for other medical imaging datasets  

**Dataset Download (via Kaggle):**  
This project uses the [Brain Tumor MRI Dataset](https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset).  

Run the following script to download the dataset:
```bash
python download_dataset.py



### Run model:
python main.py

### Folder Structure

Mega-Project/
│── Advance_Chatbot/
│   ├── chatbot.py
│   ├── requirements.txt
│   └── README.md
│
│── MRI_3D/
│   ├── download_dataset.py   # Script to fetch MRI dataset (Kaggle)
│   ├── model.py              # CNN / Deep Learning model
│   ├── data/                 # MRI dataset will be stored here
│   └── README.md
│
│── Skin_Disease/
│   ├── train.py              # Training script
│   ├── model.py              # CNN model
│   ├── dataset/              # Skin disease dataset
│   └── README.md
│
│── Smart_Diet/
│   ├── diet.py               # Recommendation logic
│   ├── data/                 # Nutritional datasets
│   └── README.md
│
│── requirements.txt
│── main.py
│── README.md
