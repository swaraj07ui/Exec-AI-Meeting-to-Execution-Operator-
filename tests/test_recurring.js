const fs = require('fs');
const path = require('path');
const assert = require('assert');

// Read the HTML file
const htmlPath = path.join(__dirname, '..', 'apps', 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

// Extract wordOverlap function
const wordOverlapMatch = html.match(/function wordOverlap\(a,b\)\{([\s\S]*?)\n\}/);
const wordOverlapSrc = wordOverlapMatch[0];

// Extract detectRecurring function
const detectRecurringMatch = html.match(/async function detectRecurring\(newTasks\)\{([\s\S]*?)\n\}/);
const detectRecurringSrc = detectRecurringMatch[0];

// Define a dummy tasks array and mock API since detectRecurring depends on them
global.tasks = [];
global.API = 'mock-api';
global.window = {};

// Mock fetch for the API call in detectRecurring
global.fetch = async (url, options) => {
    const body = JSON.parse(options.body);
    const { task1, task2 } = body.inputs;
    
    // Simple mock logic: if they contain "auth bug", consider them the same
    let is_same = false;
    if (task1.includes('auth bug') && task2.includes('auth bug')) {
        is_same = true;
    } else if (task1 === task2) {
        is_same = true;
    }
    
    return {
        ok: true,
        json: async () => ({ output: { is_same } })
    };
};

global.AbortController = class {
    constructor() { this.signal = {}; }
    abort() {}
};

// Evaluate the functions so they are available in this scope
eval(wordOverlapSrc);
eval(detectRecurringSrc);

async function runTests() {
    console.log("Running JS tests...");

    // Test 1: wordOverlap - identical titles
    let score = wordOverlap("Fix the auth bug", "Fix the auth bug");
    assert.strictEqual(score, 1, "Identical titles should have overlap 1");

    // Test 2: wordOverlap - no overlap
    score = wordOverlap("Deploy to production", "Fix the auth bug");
    assert.strictEqual(score, 0, "No overlap should have score 0");

    // Test 3: wordOverlap - stopword-only titles returning 0
    score = wordOverlap("To be or not to be", "It is what it is");
    assert.strictEqual(score, 0, "Stopword-only titles should return 0 since stopwords are filtered out");

    // Test 4: wordOverlap - partial overlap
    // "Fix the auth bug" -> filtered: fix, auth, bug (3 words)
    // "Fix the login bug" -> filtered: fix, login, bug (3 words)
    // Overlap: fix, bug (2 words) -> 2 / 3 = 0.666...
    score = wordOverlap("Fix the auth bug", "Fix the login bug");
    assert(score > 0.6 && score < 0.7, "Partial overlap should be roughly 0.66");

    // Test 5: detectRecurring - integration test with mock API
    global.tasks = [
        { id: 't1', title: "Resolve auth bug completely", status: "todo", recurrence_count: 1 }
    ];

    const newTasks = [
        { title: "Fix the auth bug", owner: "Alice" }, // Should match 't1' via API (tier 2)
        { title: "Update README", owner: "Bob" }       // Should not match anything
    ];

    const result = await detectRecurring(newTasks);
    
    assert.strictEqual(result.recurringFound.length, 1, "Should find 1 recurring task");
    assert.strictEqual(result.recurringFound[0].matchedId, 't1', "Should match t1");
    assert.strictEqual(result.recurringFound[0].count, 2, "Recurrence count should increment");
    
    assert.strictEqual(result.uniqueTasks.length, 1, "Should find 1 unique task");
    assert.strictEqual(result.uniqueTasks[0].title, "Update README", "Update README should be unique");

    console.log("All JS tests passed! ✅");
}

runTests().catch(err => {
    console.error("Test failed:", err);
    process.exit(1);
});
