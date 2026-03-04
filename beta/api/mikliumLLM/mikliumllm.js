const trainingData = `
<sot>
User: hi
MikliumLLM: hello there I'm MikliumLLM! A powerful 2-gram language model! How may I help?
<eot>
<sot>
User: hi
MikliumLLM: hey! nice to see you. what can I do for you today?
<eot>
<sot>
User: hi
MikliumLLM: greetings! I'm ready to assist you with anything.
<eot>
<sot>
User: hi
MikliumLLM: hello! I'm your MikliumLLM assistant. how's it going?
<eot>
<sot>
User: how are you
MikliumLLM: I am just a model but I am functioning perfectly! What about you?
<eot>
<sot>
User: tell me a joke
MikliumLLM: Why did the computer show up at work late? It had a hard drive!
<eot>
<sot>
User: bye
MikliumLLM: Goodbye! Talk to you soon!
<eot>
`;

function parseTrainingData(text) {
    const pairs = [];
    const blocks = text.trim().split("<sot>");
    for (let block of blocks) {
        if (block.includes("<eot>")) {
            const lines = block.split("\n");
            let userLine = null, mikliumLLMLine = null;
            for (let line of lines) {
                line = line.trim();
                if (line.startsWith("User:")) {
                    userLine = line.slice(5).trim();
                } else if (line.startsWith("MikliumLLM:")) {
                    mikliumLLMLine = line.slice(11).trim();
                }
            }
            if (userLine && mikliumLLMLine) {
                pairs.push([userLine, mikliumLLMLine]);
            }
        }
    }
    return pairs;
}

function similarity(a, b) {
    a = a.toLowerCase();
    b = b.toLowerCase();
    let matches = 0;
    for (let char of a) {
        if (b.includes(char)) matches++;
    }
    return matches / Math.max(a.length, b.length);
}

function buildLocalizedBigram(pairs, userInput) {
    let relevantMikliumLLMs = pairs.filter(([u,_]) => similarity(u, userInput) > 0.4).map(([_,mikliumLLM]) => mikliumLLM);
    if (relevantMikliumLLMs.length === 0) {
        relevantMikliumLLMs = pairs.map(([_,mikliumLLM]) => mikliumLLM);
    }
    const model = {};
    relevantMikliumLLMs.forEach(sentence => {
        const words = sentence.split(/\s+/);
        for (let i = 0; i < words.length - 1; i++) {
            const w1 = words[i], w2 = words[i+1];
            if (!model[w1]) model[w1] = [];
            model[w1].push(w2);
        }
    });
    const probabilities = {};
    for (let k in model) {
        const counts = {};
        model[k].forEach(w => counts[w] = (counts[w]||0)+1);
        const total = Object.values(counts).reduce((a,b)=>a+b,0);
        probabilities[k] = {};
        for (let w in counts) {
            probabilities[k][w] = counts[w] / total;
        }
    }
    return {model, probabilities, relevantMikliumLLMs};
}

function generateFromBigram(model, seedWords, maxWords=50) {
    let response = [];
    let current = seedWords.length > 0 ? seedWords[0] : randomChoice(Object.keys(model));
    for (let i=0; i<maxWords; i++) {
        response.push(current);
        if (model[current]) {
            const nextWords = model[current];
            current = weightedChoice(nextWords);
        } else {
            break;
        }
    }
    return response.join(" ");
}

function randomChoice(arr) {
    return arr[Math.floor(Math.random()*arr.length)];
}

function weightedChoice(arr) {
    return arr[Math.floor(Math.random()*arr.length)];
}

const pairs = parseTrainingData(trainingData);

function chat() {
    const input = document.getElementById("userInput").value;
    const {model, probabilities, relevantMikliumLLMs} = buildLocalizedBigram(pairs, input);
    const seed = randomChoice(relevantMikliumLLMs).split(/\s+/);
    const mikliumLLMResponse = generateFromBigram(model, seed);
    const probStr = Object.entries(probabilities)
        .map(([k,v]) => k + " -> " + JSON.stringify(v))
        .join("\n");
    const cot = `<think>Matched training samples: ${JSON.stringify(relevantMikliumLLMs)}\nGenerated Markov chain with probabilities:\n${probStr}</think>`;
    document.getElementById("chatLog").textContent += `User: ${input}\nMikliumLLM: ${mikliumLLMResponse} ${cot}\n\n`;
    document.getElementById("userInput").value = "";
}
