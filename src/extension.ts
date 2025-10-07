// The module 'vscode' contains the VS Code extensibility API
import * as vscode from 'vscode';
// The 'child_process' module lets us run external commands, like our Python script.
import { spawn } from 'child_process';
// The 'path' module helps us build file paths that work on any OS (Windows, macOS, etc.).
import * as path from 'path';

/**
 * This method is called when your extension is activated.
 * Your extension is activated the very first time the command is executed.
 */
export function activate(context: vscode.ExtensionContext) {

	// This is the implementation of the command we defined in package.json.
	// The commandId parameter must match the command field in package.json
	let disposable = vscode.commands.registerCommand('pygrep.searchCurrentFile', async () => {

		// 1. Get the currently active text editor
		const editor = vscode.window.activeTextEditor;
		if (!editor) {
			vscode.window.showInformationMessage('PyGrep: No active file to search.');
			return; // No open file
		}
		const filePath = editor.document.uri.fsPath;

		// 2. Prompt the user for a search pattern
		const pattern = await vscode.window.showInputBox({
			placeHolder: 'Enter regex pattern to search for...',
			prompt: 'PyGrep Search'
		});

		// If the user cancelled the input box, do nothing.
		if (!pattern) {
			return;
		}

		// 3. Create and show a dedicated output channel for our results
		const outputChannel = vscode.window.createOutputChannel("PyGrep Results");
		outputChannel.clear(); // Clear previous results
		outputChannel.show(true); // Bring the panel into view
		outputChannel.appendLine(`Searching for "${pattern}" in ${path.basename(filePath)}...\n`);

		// 4. Run the Python script as a child process

		// Construct the full path to your pygrep.py script inside the extension directory.
		const scriptPath = path.join(context.extensionPath, 'python', 'pygrep.py');

		// Prepare the arguments for the script: ['-E', 'your_pattern', 'your_file.html']
		const args = ['-E', pattern, filePath];

		// Use 'spawn' to run the command. 'python' should be in the system's PATH.
		// On Windows, you might need to use 'py' instead of 'python'.
		const pygrepProcess = spawn('python', [scriptPath, ...args]);

		// 5. Listen for output from the script

		// When the script prints a line to its standard output (stdout)...
		pygrepProcess.stdout.on('data', (data) => {
			// ...append it to our output channel in VS Code.
			outputChannel.append(data.toString());
		});

		// If the script prints any errors (stderr)...
		pygrepProcess.stderr.on('data', (data) => {
			// ...show them in the output channel for debugging.
			outputChannel.appendLine(`[ERROR] ${data.toString()}`);
		});

		// When the script finishes...
		pygrepProcess.on('close', (code) => {
			// ...log a final message.
			outputChannel.appendLine('\n-----------------------------------');
			outputChannel.appendLine(`PyGrep search finished with exit code ${code}.`);
		});
	});

	// Register our command with VS Code so it's available.
	context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
export function deactivate() { }
