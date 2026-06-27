/**
 * Chibi agent characters — rendered from real anime-chibi illustration
 * assets (PNG, transparent background) rather than hand-drawn SVG.
 * Each component renders an <img> sized to a square box so layouts
 * that expect a fixed-size chibi (StageCard, App welcome screen, etc.)
 * keep working without changes.
 */

import classifyImg from "../assets/chibi/agent_classify.png";
import coderImg from "../assets/chibi/agent_coder.png";
import reviewerImg from "../assets/chibi/agent_reviewer.png";
import researcherImg from "../assets/chibi/agent_researcher.png";
import finalizeImg from "../assets/chibi/agent_finalize.png";
import retryImg from "../assets/chibi/agent_retry.png";

import classifyHeadImg from "../assets/chibi/agent_classify_head.png";
import coderHeadImg from "../assets/chibi/agent_coder_head.png";
import reviewerHeadImg from "../assets/chibi/agent_reviewer_head.png";
import researcherHeadImg from "../assets/chibi/agent_researcher_head.png";
import finalizeHeadImg from "../assets/chibi/agent_finalize_head.png";
import retryHeadImg from "../assets/chibi/agent_retry_head.png";

function ChibiImg({ src, alt, size, bobbing, round }) {
  return (
    <img
      src={src}
      alt={alt}
      draggable={false}
      className={bobbing ? "chibi-doll" : ""}
      style={{
        height: size,
        width: round ? size : "auto",
        display: "block",
        objectFit: round ? "cover" : "contain",
        borderRadius: round ? "50%" : 0,
        filter: "drop-shadow(0 2px 6px rgba(0,0,0,0.35))",
        userSelect: "none",
      }}
    />
  );
}

// Full-body chibi — used where there's vertical room (welcome screen, final card)
export function ChibiClassify({ size = 56, bobbing = false }) {
  return <ChibiImg src={classifyImg} alt="Classify agent chibi character" size={size} bobbing={bobbing} />;
}

export function ChibiCoder({ size = 56, bobbing = false }) {
  return <ChibiImg src={coderImg} alt="Coder agent chibi character" size={size} bobbing={bobbing} />;
}

export function ChibiReviewer({ size = 56, bobbing = false }) {
  return <ChibiImg src={reviewerImg} alt="Reviewer agent chibi character" size={size} bobbing={bobbing} />;
}

export function ChibiResearcher({ size = 56, bobbing = false }) {
  return <ChibiImg src={researcherImg} alt="Researcher agent chibi character" size={size} bobbing={bobbing} />;
}

export function ChibiFinalize({ size = 56, bobbing = false }) {
  return <ChibiImg src={finalizeImg} alt="Finalize agent chibi character" size={size} bobbing={bobbing} />;
}

export function ChibiRetry({ size = 48, bobbing = false }) {
  return <ChibiImg src={retryImg} alt="Retry agent chibi character" size={size} bobbing={bobbing} />;
}

// Round headshot crop — used in tight spaces like the StageCard header
export function ChibiClassifyHead({ size = 44, bobbing = false }) {
  return <ChibiImg src={classifyHeadImg} alt="Classify agent" size={size} bobbing={bobbing} round />;
}

export function ChibiCoderHead({ size = 44, bobbing = false }) {
  return <ChibiImg src={coderHeadImg} alt="Coder agent" size={size} bobbing={bobbing} round />;
}

export function ChibiReviewerHead({ size = 44, bobbing = false }) {
  return <ChibiImg src={reviewerHeadImg} alt="Reviewer agent" size={size} bobbing={bobbing} round />;
}

export function ChibiResearcherHead({ size = 44, bobbing = false }) {
  return <ChibiImg src={researcherHeadImg} alt="Researcher agent" size={size} bobbing={bobbing} round />;
}

export function ChibiFinalizeHead({ size = 44, bobbing = false }) {
  return <ChibiImg src={finalizeHeadImg} alt="Finalize agent" size={size} bobbing={bobbing} round />;
}

export function ChibiRetryHead({ size = 40, bobbing = false }) {
  return <ChibiImg src={retryHeadImg} alt="Retry agent" size={size} bobbing={bobbing} round />;
}
