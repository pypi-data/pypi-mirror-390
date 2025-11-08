# LaTeX Style File Contracts

This document defines the standard interface and behavior contracts for general-purpose LaTeX style files in this repository.

## Overview

Each style file (`.sty`) in this repository is adapted from academic conference templates to be general-purpose while maintaining the original formatting and appearance. They all follow a consistent contract for options, metadata, and behavior.

## Standard Options

All style files support these document class options:

### Status Options (Mutually Exclusive)

- **`final`** (default): Final version of the document
  - No line numbers
  - Full author information displayed
  - Clean, publication-ready output

- **`confidential`**: Marks document as confidential
  - Adds "CONFIDENTIAL" label/footnote
  - May include metadata in header or footnote

- **`internal`**: Marks document for internal use only
  - Adds "INTERNAL USE ONLY" label/footnote
  - May include metadata in header or footnote

- **`draft`**: Draft version with review markings
  - Displays line numbers (left margin)
  - May show draft watermarks or labels
  - Helpful for collaborative editing and review

### Additional Options

- **`review`**: Conference-specific review mode (ACL, ICLR, NeurIPS)
  - Enables line numbers
  - May anonymize authors for blind review
  - Behavior varies by style

## Metadata Commands

All style files provide these commands for document metadata. **Note:** The placement and display of metadata is style-dependent - each style uses the most appropriate method for its layout and conventions.

### `\setorganization{text}`

Sets the organization/company name.

**Example:**

```latex
\setorganization{Acme Corporation}
```

**Display:** Style-dependent. Typically shown in small caps.

### `\setdoctype{text}`

Sets the document type or category.

**Example:**

```latex
\setdoctype{Research Report}
\setdoctype{Technical Specification}
\setdoctype{Quarterly Review}
```

**Display:** Style-dependent. Typically shown in regular text.

### `\setdocid{text}`

Sets the document ID or reference number.

**Example:**

```latex
\setdocid{DOC-2024-001}
\setdocid{CONF-2024-042}
\setdocid{REP-Q3-2024}
```

**Display:** Style-dependent. Typically shown in monospace or regular font.

## Style-Specific Behaviors

Each style file implements metadata display in the way that best fits its original design and conventions. The metadata placement varies by style to maintain the authentic look and feel of each template.

### NeurIPS Style (`neurips.sty`)

**Metadata Placement:** Full-width footer at bottom of first page

**Why this placement?** NeurIPS is a single-column format with ample bottom margin space. A footer provides clear separation from content while being immediately visible.

**Format:**

```text
STATUS • ORGANIZATION — Document Type — DOC-ID
```

**Example:**

```text
CONFIDENTIAL • ACME CORPORATION — Research Report — DOC-2024-001
```

**Styling:**

- Status label in **bold** with bullet separator
- Organization in **small caps**
- Document type and ID in regular text
- Positioned 0.3in from bottom of page
- Spans full paper width (not just text width)

**Line Numbers:** Left margin in draft mode

**Usage:**

```latex
\documentclass{article}
\usepackage[confidential]{neurips}

\setorganization{Acme Corporation}
\setdoctype{Research Report}
\setdocid{DOC-2024-001}

\title{My Document}
\author{John Doe}

\begin{document}
\maketitle
...
\end{document}
```

### ICLR Style (`iclr.sty`)

**Metadata Placement:** Header on all pages using tabularx

**Why this placement?** ICLR is a single-column format with a traditional header area. Headers provide consistent visibility across all pages and don't interfere with the body content.

**Format:**

```text
STATUS    ORGANIZATION    Document Type    DOC-ID
```

**Styling:**

- Status in **bold**
- Organization in **small caps**
- Document Type in regular text (X column, expands to fill)
- DOC-ID right-aligned in regular text
- Tabular layout with 1em spacing between columns
- Spans full text width

**Line Numbers:** Left margin when `draft` option is used

**Special Features:**

- Loads `newtxtext` package for Times-compatible fonts (XeTeX/LuaTeX compatible)
- Includes `\begin{ack}...\end{ack}` environment for acknowledgments

**Usage:**

```latex
\documentclass{article}
\usepackage[draft]{iclr}

\setorganization{Research Lab}
\setdoctype{Draft Proposal}
\setdocid{DRAFT-2024-15}

\title{My Research}
\author{Jane Smith}

\begin{document}
\maketitle

\begin{abstract}
...
\end{abstract}

\section{Introduction}
...

\begin{ack}
We thank our collaborators...
\end{ack}

\end{document}
```

### ACL Style (`acl.sty`)

**Metadata Placement:** Footnote on first page

**Why this placement?** ACL is a two-column format where headers and footers would disrupt the compact layout. Footnotes are the traditional ACL mechanism for auxiliary information (author affiliations, acknowledgments, etc.).

**Format:** User must call `\aclmetadata` within the `\author{}` command:

```text
¹ STATUS — ORGANIZATION — Document Type — DOC-ID
```

**Styling:**

- Status in **bold** with em-dash separators
- Organization in **small caps**
- Document type and ID in regular text
- Appears as a standard footnote marker and text
- Only on first page

**Line Numbers:** Left margin when `draft` or `review` option is used

**Special Features:**

- Two-column layout (standard ACL format)
- Automatically loads required packages: `times`, `latexsym`, `fontenc`, `inputenc`, `microtype`
- Compatible with ACL bibliography styles
- Requires `\documentclass[11pt]{article}` for proper formatting
- **Important:** User must manually add `\aclmetadata` to author field

**Usage:**

```latex
\documentclass[11pt]{article}
\usepackage[confidential]{acl}

\setorganization{Acme Corporation}
\setdoctype{Confidential Analysis}
\setdocid{CONF-2024-042}

\title{My Analysis}
\author{Strategic Planning Team\aclmetadata}  % Note: \aclmetadata required!

\begin{document}
\maketitle

\begin{abstract}
...
\end{abstract}

\section{Introduction}
...

\end{document}
```

## Design Principles

All style files in this repository follow these principles:

### 1. **NEVER Modify Original Styles**

**This is the most critical principle.** When adapting a style file:

**DO NOT change:**

- ❌ Font families, sizes, or weights
- ❌ Line spacing, paragraph spacing, or margins
- ❌ Page layout, column widths, or text width
- ❌ Section heading styles or formatting
- ❌ List spacing or indentation
- ❌ Math or equation formatting
- ❌ Bibliography or citation styles
- ❌ Any visual appearance of the document

**The original style must be preserved completely.** Users choose these styles because they want the specific appearance of NeurIPS, ICLR, ACL, etc. Any changes to fonts, spacing, or layout would make the style inauthentic.

**Verification:** Before and after adding functionality, compile the same document with both the original and modified style files. The output PDFs should be **pixel-identical** except for the added metadata display.

### 2. Include Required Packages in Style File

**DO include in the `.sty` file:**

- ✅ Fonts required by the original template (e.g., `times`, `newtxtext`)
- ✅ Encoding packages needed for proper rendering (`fontenc`, `inputenc`)
- ✅ Typography packages that are standard for the style (`microtype`, `latexsym`)
- ✅ Layout packages the style depends on (`geometry`, `fancyhdr`)
- ✅ Packages for added functionality (if minimal and safe)

**Use safe loading:**

```latex
% Check if package is already loaded to avoid conflicts
\@ifpackageloaded{times}{}{\usepackage{times}}
\@ifpackageloaded{fontenc}{}{\usepackage[T1]{fontenc}}
```

**Why include packages in `.sty`?**

- Makes the style file self-contained and easier to use
- Ensures correct fonts and encoding are always loaded
- Prevents users from forgetting required packages
- Maintains consistency across all documents using the style

**When NOT to include:**

- User-preference packages (e.g., `graphicx`, `amsmath`, `algorithm2e`)
- Packages that might conflict with user's choices
- Packages not required by the original template

### 3. Non-Breaking Additions

- New options are opt-in
- Metadata commands are optional
- Documents compile correctly without any metadata set

### 3. Consistent Interface

- Same option names across all styles (`confidential`, `internal`, `draft`, `final`)
- Same metadata commands (`\setorganization`, `\setdoctype`, `\setdocid`)
- Predictable behavior

### 4. Style-Appropriate Implementation

**Metadata placement is style-dependent.** Each style uses the method that best fits its original design:

- **NeurIPS**: Footer (single-column layout with ample bottom margin)
- **ICLR**: Header (single-column with traditional header area)
- **ACL**: Footnote (two-column compact layout where headers would be disruptive)

**Rationale:** Rather than forcing a uniform approach, each style implements metadata in the way that:

- Respects the original template's design philosophy
- Fits naturally within the layout constraints
- Maintains the authentic appearance of the style
- Uses mechanisms already present in the original (e.g., ACL uses footnotes for affiliations)

Line numbers use each style's native implementation and appear only in draft/review modes.

### 5. Safe Package Loading

- Use `\@ifpackageloaded` to check before loading packages
- Avoid conflicts with user's preamble
- Load only essential packages for the style
- Always use safe loading patterns as shown in Principle 2

## Critical Guidelines for Style Developers

When creating or modifying a style file, you **must**:

1. **Start from the original** - Copy the original `.sty` file, never build from scratch
2. **Test with original examples** - Compile the original template examples to verify appearance
3. **Compare outputs** - Use `diff` or visual comparison to ensure no unintended changes
4. **Document packages** - List all packages you include and why they're necessary
5. **Test without metadata** - Verify documents compile correctly with empty metadata
6. **Preserve all commands** - Don't remove or modify existing commands from the original
7. **Use minimal additions** - Only add what's necessary for the contract functionality

**Red flags that indicate you're breaking the principles:**

- 🚨 File size of compiled PDF changes significantly
- 🚨 Fonts look different from original template
- 🚨 Text is wider/narrower or pages break differently
- 🚨 Spacing between sections or paragraphs changes
- 🚨 Original examples from the template don't compile
- 🚨 Warning messages about font substitution appear

## Common Patterns

### Empty Metadata Handling

When metadata is not set, it is simply omitted from display:

```latex
% Only status, no other metadata
\usepackage[confidential]{neurips}
% Displays: CONFIDENTIAL
```

```latex
% Status and organization only
\usepackage[draft]{iclr}
\setorganization{My Company}
% Displays: DRAFT    MY COMPANY
```

### Multiple Document Compilation

All styles support standard LaTeX compilation:

```bash
# Using tectonic (recommended)
tectonic document.tex

# Using pdflatex
pdflatex document.tex

# Using xelatex (works best with ICLR style)
xelatex document.tex
```

### Compatibility Notes

- **NeurIPS**: Works with all TeX engines
- **ICLR**: Optimized for XeTeX/LuaTeX (uses OpenType fonts)
- **ACL**: Requires `pdflatex` or compatible (uses legacy font system)

## Testing Checklist

When creating or modifying a style file, verify:

### Functionality Tests

- [ ] All four options work: `final`, `confidential`, `internal`, `draft`
- [ ] Metadata commands work individually and in combination
- [ ] Empty metadata doesn't break compilation
- [ ] Line numbers appear in draft mode only
- [ ] Examples compile without errors

### Style Preservation Tests (CRITICAL)

- [ ] **Compile original template example** - Use the unmodified `.sty` and original `.tex` example
- [ ] **Compile with modified style** - Use your `.sty` with the same `.tex` example
- [ ] **Compare PDFs visually** - They should look identical (except metadata)
- [ ] **Check file sizes** - Should be nearly identical (within 1-2KB)
- [ ] **No font warnings** - No "Font shape not available" or substitution warnings
- [ ] **Text width identical** - Measure text block, should match exactly
- [ ] **Line breaks identical** - Same line breaks in paragraphs and sections
- [ ] **Page breaks identical** - Same number of pages, same content per page

### Package Loading Tests

- [ ] Package conflicts are avoided
- [ ] Safe loading (`\@ifpackageloaded`) is used
- [ ] Required fonts are included in `.sty`
- [ ] Style compiles without user loading additional packages
- [ ] No duplicate package loading warnings

### Documentation Tests

- [ ] Style-specific behaviors documented in this file
- [ ] Examples include comments explaining metadata usage
- [ ] README or comments explain any special requirements

## Future Extensions

New style files should:

1. Follow the same option and metadata contract
2. Document any style-specific behaviors
3. Provide at least 3 examples (final, confidential, draft)
4. Update this contract document with style-specific details
