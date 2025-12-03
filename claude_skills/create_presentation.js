const PptxGenJS = require('pptxgenjs');

const prs = new PptxGenJS();
prs.layout = 'LAYOUT_16x9';
prs.author = 'Claude Code';
prs.title = 'Space Exploration';

// Slide 1: Title
let slide = prs.addSlide();
slide.background = { color: '0a1628' };
slide.addText('Space Exploration', {
  x: 0.5, y: 1.5, w: 9, h: 1,
  fontSize: 54, bold: true, color: '00d9ff',
  align: 'center', fontFace: 'Arial'
});
slide.addText('Journey Beyond Earth', {
  x: 0.5, y: 2.8, w: 9, h: 0.6,
  fontSize: 28, color: 'e0e0e0',
  align: 'center', fontFace: 'Arial'
});

// Slide 2: Key Milestones
slide = prs.addSlide();
slide.background = { color: '0a1628' };
slide.addShape(prs.ShapeType.rect, {
  x: 0, y: 0, w: 10, h: 0.6,
  fill: { color: '00d9ff' }
});
slide.addText('Key Milestones', {
  x: 0.5, y: 0.1, w: 9, h: 0.5,
  fontSize: 32, bold: true, color: '0a1628',
  align: 'center', fontFace: 'Arial'
});
const milestones = [
  'Moon Landing (1969)',
  'Space Shuttle Era (1981-2011)',
  'International Space Station (1998-present)',
  'Mars Rovers (2004-present)',
  'Private Space Companies (2010-present)'
];
let y = 1.2;
milestones.forEach(milestone => {
  slide.addText('★ ' + milestone, {
    x: 1, y: y, w: 8, h: 0.5,
    fontSize: 16, color: 'ffffff',
    fontFace: 'Arial'
  });
  y += 0.55;
});

// Slide 3: Solar System
slide = prs.addSlide();
slide.background = { color: '0a1628' };
slide.addShape(prs.ShapeType.rect, {
  x: 0, y: 0, w: 10, h: 0.6,
  fill: { color: '9b59b6' }
});
slide.addText('Our Solar System', {
  x: 0.5, y: 0.1, w: 9, h: 0.5,
  fontSize: 32, bold: true, color: 'ffffff',
  align: 'center', fontFace: 'Arial'
});

const planets = [
  { name: 'Mercury', fact: 'Closest to Sun', x: 0.5 },
  { name: 'Venus', fact: 'Hottest Planet', x: 3.5 },
  { name: 'Earth', fact: 'Our Home', x: 6.5 },
  { name: 'Mars', fact: 'Red Planet', x: 0.5 },
  { name: 'Jupiter', fact: 'Giant Planet', x: 3.5 },
  { name: 'Saturn', fact: 'Ring System', x: 6.5 }
];

let row = 0;
for (let i = 0; i < planets.length; i++) {
  if (i === 3) row = 1;
  const planet = planets[i];
  const py = 1.3 + (row * 1.8);

  slide.addShape(prs.ShapeType.rect, {
    x: planet.x, y: py, w: 2.5, h: 1.5,
    fill: { color: '1a3a52' },
    line: { color: '00d9ff', width: 2 }
  });

  slide.addText(planet.name, {
    x: planet.x, y: py + 0.2, w: 2.5, h: 0.4,
    fontSize: 14, bold: true, color: '00d9ff',
    align: 'center', fontFace: 'Arial'
  });

  slide.addText(planet.fact, {
    x: planet.x, y: py + 0.7, w: 2.5, h: 0.6,
    fontSize: 12, color: 'e0e0e0',
    align: 'center', fontFace: 'Arial'
  });
}

// Slide 4: The Future
slide = prs.addSlide();
slide.background = { color: '0a1628' };
slide.addShape(prs.ShapeType.rect, {
  x: 0, y: 0, w: 10, h: 0.6,
  fill: { color: '00d9ff' }
});
slide.addText('The Future', {
  x: 0.5, y: 0.1, w: 9, h: 0.5,
  fontSize: 32, bold: true, color: '0a1628',
  align: 'center', fontFace: 'Arial'
});

slide.addShape(prs.ShapeType.rect, {
  x: 2, y: 1.5, w: 6, h: 2,
  fill: { color: '2a1a4a' },
  line: { color: '9b59b6', width: 2 }
});

slide.addText('Next Frontier', {
  x: 2, y: 1.8, w: 6, h: 0.5,
  fontSize: 24, bold: true, color: '9b59b6',
  align: 'center', fontFace: 'Arial'
});

slide.addText('Human missions to Mars\nLunar base establishment\nDeep space exploration', {
  x: 2.2, y: 2.5, w: 5.6, h: 1,
  fontSize: 14, color: 'e0e0e0',
  align: 'center', fontFace: 'Arial'
});

// Save presentation
prs.writeFile({ fileName: 'space_exploration.pptx' });
console.log('✓ Presentation created successfully: space_exploration.pptx');
