import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));

// Base paths
export const SKILLS_DIR = join(__dirname, "../../..", "skills");
export const BUILD_DIR = join(__dirname, "..");

// Skill configurations
export interface SkillConfig {
  name: string;
  title: string;
  description: string;
  skillDir: string;
  rulesDir: string;
  metadataFile: string;
  outputFile: string;
  sectionMap: Record<string, number>;
}

export const SKILLS: Record<string, SkillConfig> = {
  "create-and-publish-study": {
    name: "create-and-publish-study",
    title: "Create and Publish Study",
    description: "CLI skill for creating and publishing Prolific research studies",
    skillDir: join(SKILLS_DIR, "create-and-publish-study"),
    rulesDir: join(SKILLS_DIR, "create-and-publish-study/rules"),
    metadataFile: join(SKILLS_DIR, "create-and-publish-study/metadata.json"),
    outputFile: join(SKILLS_DIR, "create-and-publish-study/AGENTS.md"),
    sectionMap: { auth: 1, create: 2, publish: 3, errors: 4 },
  },
  "examine-participant-messages": {
    name: "examine-participant-messages",
    title: "Examine Participant Messages",
    description: "Participant message analysis for Prolific AI tasks",
    skillDir: join(SKILLS_DIR, "examine-participant-messages"),
    rulesDir: join(SKILLS_DIR, "examine-participant-messages/rules"),
    metadataFile: join(
      SKILLS_DIR,
      "examine-participant-messages/metadata.json",
    ),
    outputFile: join(SKILLS_DIR, "examine-participant-messages/AGENTS.md"),
    sectionMap: {},
  },
};

// Default skill
export const DEFAULT_SKILL = "create-and-publish-study";
