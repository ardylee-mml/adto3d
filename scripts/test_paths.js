const fs = require('fs');
const path = require('path');
const axios = require('axios');

// Test directories
const directories = {
    uploads: path.join(process.cwd(), 'uploads'),
    outputs: path.join(process.cwd(), 'outputs'),
    logs: path.join(process.cwd(), 'logs')
};

// Create test files
async function createTestFiles() {
    console.log('Creating test files...');

    // Create test GLB file in outputs
    const testGlb = path.join(directories.outputs, 'test.glb');
    fs.writeFileSync(testGlb, 'test GLB content');
    console.log('Created test GLB file:', testGlb);

    // Create test image in uploads
    const testImage = path.join(directories.uploads, 'test.png');
    fs.writeFileSync(testImage, 'test image content');
    console.log('Created test image:', testImage);
}

// Test paths
async function testPaths() {
    const baseUrl = 'http://localhost:3000';

    try {
        // Test outputs path
        console.log('\nTesting /outputs path...');
        const outputsResponse = await axios.get(`${baseUrl}/outputs/test.glb`);
        console.log('Outputs path response:', outputsResponse.status);
        console.log('Content-Type:', outputsResponse.headers['content-type']);

        // Test uploads path
        console.log('\nTesting /api/files/uploads path...');
        const uploadsResponse = await axios.get(`${baseUrl}/api/files/uploads/test.png`);
        console.log('Uploads path response:', uploadsResponse.status);

        console.log('\nAll paths tested successfully!');
    } catch (error) {
        console.error('Error testing paths:', error.message);
        if (error.response) {
            console.error('Response status:', error.response.status);
            console.error('Response headers:', error.response.headers);
        }
    }
}

// Clean up test files
function cleanup() {
    console.log('\nCleaning up test files...');
    try {
        fs.unlinkSync(path.join(directories.outputs, 'test.glb'));
        fs.unlinkSync(path.join(directories.uploads, 'test.png'));
        console.log('Test files cleaned up successfully!');
    } catch (error) {
        console.error('Error cleaning up:', error.message);
    }
}

// Run tests
async function runTests() {
    try {
        await createTestFiles();
        await testPaths();
    } finally {
        cleanup();
    }
}

runTests(); 