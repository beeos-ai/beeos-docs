import fs from "node:fs";

const [specPath, runtimeErrorCodesPath] = process.argv.slice(2);

if (!specPath || !runtimeErrorCodesPath) {
  throw new Error("usage: inline-openapi-refs.mjs <spec> <runtime-error-codes>");
}

const externalRef = "{ $ref: './runtime-error-codes-v4.generated.json' }";
const schema = JSON.parse(fs.readFileSync(runtimeErrorCodesPath, "utf8"));
const spec = fs.readFileSync(specPath, "utf8");
const occurrences = spec.split(externalRef).length - 1;

if (occurrences === 0) {
  throw new Error(`expected external runtime error-code refs in ${specPath}`);
}

// Mintlify rejects external OpenAPI refs, so emit an equivalent self-contained spec.
fs.writeFileSync(specPath, spec.replaceAll(externalRef, JSON.stringify(schema)));
process.stdout.write(`  inlined ${occurrences} runtime error-code reference(s)\n`);
