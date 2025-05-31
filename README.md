# AI_1_Project
RAG

Temporary readme:
🎓 Kontext:
Du hjälper till att bygga ett skolprojekt i AI-kursen AI-1. Projektet ska visa att studenten förstått och tillämpat LLM-teknik på ett realistiskt, avgränsat och tekniskt moget sätt.

🧠 Projektidé:
Skapa en fungerande och användbar RAG-lösning (Retrieval-Augmented Generation) för ett fiktivt finansbolag. Systemet ska möjliggöra frågor kring interna dokument (t.ex. leasingavtal, kreditvillkor, interna policies) där användaren får tydliga svar med stöd i dokumentens innehåll.

🚫 **Ingen användning av OpenAI eller externa API:er** får ske – allt körs lokalt via `Ollama` för att uppfylla GDPR och datasuveränitet.

🧱 Teknikstack:
- 🧠 LLM: Mistral 7B Instruct, körs lokalt via **Ollama**
- 📚 RAG: LlamaIndex eller LangChain
- 📦 Vectorstore: **ChromaDB** (lokal SQLite-backend)
- 🧑‍💻 Gränssnitt: **Streamlit** med formulär för fråga & svar
- 🧪 Testdata: Fiktiva PDF/Word-kontrakt, leasingvillkor, kreditpolicy
- 🔁 Extra (VG-nivå): Automatiserade arbetsflöden med **n8n** (valfritt)

🎯 MVP-mål:
- Dokument laddas upp och delas upp i chunks
- Embeddings skapas och lagras i ChromaDB
- Användare skriver en fråga
- Systemet returnerar ett svar **baserat på dokumentinnehåll**
- Om inget träffas: “Jag hittar ingen relevant information i tillgängliga dokument.”

⚠️ Teknikrisker som ska prioriteras tidigt:
- Embedding och chunking fungerar korrekt (testas med dummyavtal)
- LLM-modellen klarar svara korrekt med rätt promptstyrning
- Lokalt API från Ollama integreras utan nätverksproblem
- UI är tydligt nog för demo, även utan tung front-end

🧠 VG-nivå (om möjligt):
- Integrera n8n för t.ex:
  - Automatisk dokumentuppladdning
  - Skicka AI-svar via e-post
  - Skapa Slack-varning vid riskklausul
- Alternativt: jämförelse mellan två olika LLM-modeller lokalt
- Extra GUI-komponenter eller jämförande analys i rapporten

🧪 Datakrav:
- Skapa egna dummy-dokument (t.ex. 3–5 PDF med olika paragrafer och villkor)
- Formulera exempel-promptar/användarfrågor
- Definiera vad som är ett korrekt svar

📋 Projektkrav från kurs:
- Projektet ska genomföras i Trello/Jira och visas i två standups
- Teknikrisker ska testas och åtgärdas tidigt (”släcka dem”)
- Projektet ska vara klart att demonstrera inom utsatt tid
- En rapport ska lämnas in tillsammans med kod

📣 Viktigt:
Projektet får inte vara en enkel “chatbot med LLM”, utan måste:
- Ha domänspecifik användning
- Ha tydlig MVP
- Inkludera interaktion, datastruktur eller automation

📌 Starta med att:
1. Skapa en taskboard (Trello) och bryt ned komponenter
2. Testa att du kan köra Mistral via `ollama run mistral`
3. Bygg en enkel loop: [dokument] → [embedding] → [RAG-svar]

🎯 Ditt mål: att skapa en tekniskt mogen, användbar, lokal AI-applikation inom ramen för ett verkligt problem — utan att överskrida realistisk skolprojektsnivå.
