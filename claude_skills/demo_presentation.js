const PptxGenJS = require('pptxgenjs');

const prs = new PptxGenJS();
prs.layout = 'LAYOUT_16x9';
prs.author = 'Claude Code';
prs.title = 'Arbitrary Skill Demonstration';

// Slide 1: Title
let slide = prs.addSlide();
slide.background = { color: '1a1a1a' };
slide.addText('Arbitrary Skill Demonstration', {
  x: 0.5, y: 1.0, w: 9, h: 1.0,
  fontSize: 34, bold: true, color: 'FFFFFF',
  align: 'center', fontFace: 'Arial'
});
slide.addText('Demonstrating use of tooling to achieve code-driven results', {
  x: 0.5, y: 2.2, w: 9, h: 0.8,
  fontSize: 18, color: 'CFCFCF', align: 'center', fontFace: 'Arial'
});

// Slide 2: Plan
slide = prs.addSlide();
slide.background = { color: '1a1a1a' };
slide.addShape(prs.ShapeType.rect, {
  x: 0, y: 0, w: 10, h: 0.6,
  fill: { color: '00d9ff' }
});
slide.addText('Plan', {
  x: 0.5, y: 0.1, w: 9, h: 0.5,
  fontSize: 28, bold: true, color: '1a1a1a',
  align: 'center', fontFace: 'Arial'
});
slide.addText('- Inspect current codebase\\n- Propose minimal, targeted edits\\n- Apply changes with precise diffs\\n- Validate results', {
  x: 1, y: 1.0, w: 8, h: 3,
  fontSize: 14, color: 'ffffff', align: 'left', fontFace: 'Arial'
});

// Slide 3: Verification
slide = prs.addSlide();
slide.background = { color: '1a1a1a' };
slide.addShape(prs.ShapeType.rect, {
  x: 0, y: 0, w: 10, h: 0.6,
  fill: { color: '00d9ff' }
});
slide.addText('Verification', {
  x: 0.5, y: 0.1, w: 9, h: 0.5,
  fontSize: 28, bold: true, color: '1a1a1a',
  align: 'center', fontFace: 'Arial'
});
slide.addText('This deck is generated entirely from code to demonstrate automation-based storytelling.', {
  x: 0.8, y: 1.0, w: 8.4, h: 2.0,
  fontSize: 14, color: 'ffffff', align: 'left', fontFace: 'Arial'
});

// Save presentation
prs.writeFile({ fileName: 'arbitrary_skill_demo.pptx' });
console.log('Presentation created: arbitrary_skill_demo.pptx');
