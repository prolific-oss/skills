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
  "prolific-api": {
    name: "prolific-api",
    title: "Prolific API Integration",
    description: "Prolific API integration patterns for AI research workflows",
    skillDir: join(SKILLS_DIR, "prolific-api"),
    rulesDir: join(SKILLS_DIR, "prolific-api/rules"),
    metadataFile: join(SKILLS_DIR, "prolific-api/metadata.json"),
    outputFile: join(SKILLS_DIR, "prolific-api/AGENTS.md"),
    sectionMap: { auth: 1, approve: 2, bonuses: 3, rate: 4, errors: 5 },
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
export const DEFAULT_SKILL = "prolific-api";
