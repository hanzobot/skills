#!/usr/bin/env node
/**
 * Hanzo Bot Client - For Agent Zero to call Hanzo Bot
 * 
 * Usage:
 *   node bot_client.js <message>
 *   node bot_client.js message <text>
 *   node bot_client.js notify <text>
 *   node bot_client.js tool <name> <json>
 * 
 * Environment:
 *   BOT_API_URL   - Gateway URL (default: http://127.0.0.1:18789)
 *   BOT_API_TOKEN - Gateway auth token (required)
 *   DOCKER_CONTAINER   - Set to "true" if running inside Docker
 */

const Hanzo BotClient = require('./lib/bot_api');
const { parseArgs } = require('./lib/cli');

const HELP = `
Hanzo Bot Client (Agent Zero → Hanzo Bot)

Usage:
  node bot_client.js <message>
  node bot_client.js message <text>    - Send message, get response
  node bot_client.js notify <text>     - Send notification
  node bot_client.js tool <name> <json> - Invoke a Hanzo Bot tool

Environment:
  BOT_API_URL       - Gateway URL (default: http://127.0.0.1:18789)
  BOT_API_URL_DOCKER - URL when running in Docker (use host IP)
  BOT_API_TOKEN     - Gateway auth token (required)
  DOCKER_CONTAINER       - Set to "true" if running inside Docker

Examples:
  node bot_client.js "Task complete!"
  node bot_client.js notify "Progress: 50%"
  node bot_client.js tool sessions_list '{}'
`;

async function main() {
    const parsed = parseArgs(process.argv.slice(2));
    const commands = ['message', 'notify', 'tool', 'help'];
    
    // Default to message if command not recognized
    if (parsed.command && !commands.includes(parsed.command)) {
        parsed.args.unshift(parsed.command);
        parsed.command = 'message';
    }

    if (!parsed.command || parsed.command === 'help' || parsed.options.help) {
        console.log(HELP);
        return;
    }

    const client = new Hanzo BotClient();

    try {
        let result;
        const text = parsed.args.join(' ');

        switch (parsed.command) {
            case 'message':
                if (!text) {
                    console.error("Error: Provide a message");
                    process.exit(1);
                }
                result = await client.sendMessage(text, { 
                    prefix: '[FROM AGENT ZERO]',
                    timeout: parsed.options.timeout 
                });
                break;

            case 'notify':
                if (!text) {
                    console.error("Error: Provide a notification");
                    process.exit(1);
                }
                result = await client.notify(text);
                result = typeof result === 'string' ? result : JSON.stringify(result, null, 2);
                break;

            case 'tool':
                const toolName = parsed.args[0];
                if (!toolName) {
                    console.error("Error: Provide tool name");
                    process.exit(1);
                }
                const toolArgs = parsed.args[1] ? JSON.parse(parsed.args[1]) : {};
                result = await client.invokeTool(toolName, toolArgs);
                result = JSON.stringify(result, null, 2);
                break;

            default:
                console.error(`Unknown command: ${parsed.command}`);
                process.exit(1);
        }

        console.log(result);

    } catch (error) {
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
}

main();
