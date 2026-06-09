import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function main() {
  const transport = new StdioClientTransport({
    command: "npx",
    args: ["-y", "pexels-mcp-server"]
  });
  
  const client = new Client({ name: "test-client", version: "1.0.0" });
  await client.connect(transport);
  
  const tools = await client.listTools();
  console.log(JSON.stringify(tools, null, 2));
  
  await transport.close();
}
main().catch(console.error);
