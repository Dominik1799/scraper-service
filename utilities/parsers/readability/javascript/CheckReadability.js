/*
 * This file is part of ReadabiliPy
 */

const fs = require('fs');
const { isProbablyReaderable } = require('@mozilla/readability');
const { JSDOM } = require('jsdom');
const { exit } = require('process');

function readFile(filePath) {
	return fs.readFileSync(filePath, {encoding: "utf-8"}).trim();
}


function main() {

	var argv = require('minimist')(process.argv.slice(2));
	if (argv['i'] === undefined) {
		console.log("Input file required.");
		return 1;
	}

	var inFilePath = argv['i'];

	var html = readFile(inFilePath);
	var doc = new JSDOM(html);
	if (isProbablyReaderable(doc.window.document, { minScore: 20 })) {
		return 0;
	} else {
		return exit(1);
	}
}

main();
