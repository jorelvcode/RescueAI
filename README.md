# RescueAI

<img width="345" alt="RescueAI_logo" src="https://github.com/user-attachments/assets/dc09267f-c707-40a9-a69d-827f3c0fbcf8" />

## Introduction

Welcome to RescueAI, the AI-powered 911 operator assistant made to make dispatch easy!

## Contributors

![image](https://github.com/user-attachments/assets/0b97810f-6f49-4905-9d9a-a0c405444510)

## The Problem

Emergency dispatchers work for long hours at a time in high-stress environments, constantly handling emergency situations and manually entering data at the same time. Such stress may lead to a loss in focus, an increase in errors, and, coupled with the gruntwork, inefficiencies in their performance. 

Unfortunately, there can be no room for error, especially in a field where lives are at stake. 

## The Solution

To address this problem, we created RescueAI, an AI-powered 911 operator assistant. It has two features that do so: 
- a **live keyword extractor**, meant for use in tandem with a 911 operator’s computer-aided dispatch (CAD) system to list information crucial for dispatch
- a **chatbot**, which answers the user's protocol questions based on a comprehensive protocol document relevant to their jurisdiction.

RescueAI helps relieve the burden that comes with a 911 operator's job, reducing stress, minimizing errors, and promoting efficiency.

## Demo Video

To see a demonstration of how RescueAI works, watch our demo video here: 

[![RescueAI Demo Vid](https://github.com/user-attachments/assets/89ad9c1e-2246-421c-be11-7b6933777ee2)](https://youtu.be/8WYtjIdxLEk?si=c6HTdkEfZu_3FTR0)

## Application Design

RescueAI utilizes a number of items in regards to its application design:
- The chatbot feature is meant to reference jurisdiction-specific 911 operator protocol documents for its answers. As a substitute, two synthetic protocol documents have been provided.
- The chatbot feature is powered by OpenAI's GPT-4.
- The keyword extraction feature is powered by OpenAI's GPT-4 and Whisper.
- The application as a whole is written in Python and hosted on a Streamlit website.

## Ethical Design

RescueAI was developed with ethics in mind: 
- Because it references specific documents only, AI hallucinations are unlikely, and biases from outside sources are eliminated.
- One of our goals is to keep the human aspect of the 911 operator job; we aim to simply relieve their burden and not replace the person.

### Thank you for reading until the end--we hope you enjoy RescueAI!
