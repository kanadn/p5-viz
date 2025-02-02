// Global configuration
let particles = [];
const numParticles = 25;

// Cylinder container dimensions
const cylRadius = 200;
const cylHeight = 400;

// Outer spherical container radius: must fully enclose the cylinder.
// We use the distance from the center to a cylinder corner.
const sphereRadius = Math.sqrt(cylRadius * cylRadius + (cylHeight / 2) ** 2) + 20;

let rotAngle = 0;         // Rotation angle for the container
let zoomFactor = 1;       // Global zoom factor

function setup() {
  createCanvas(windowWidth, windowHeight, WEBGL);
  // Create particles with random positions and velocities inside the cylinder.
  for (let i = 0; i < numParticles; i++) {
    particles.push(new Particle());
  }
  // Use smooth drawing
  smooth();
}

function draw() {
  // Draw a translucent black background so old trails slowly fade.
  // (The alpha here controls the trail persistence.)
  background(0);

  // Update global rotation and zoom values.
  rotAngle += 0.005; // slow rotation
  zoomFactor = 1 + 0.3 * sin(frameCount * 0.005); // oscillate zoom

  // Apply global transformations: zoom and rotate the scene.
  push();
  scale(zoomFactor);
  rotateY(rotAngle);
  ambientLight(150);
  directionalLight(255, 255, 255, 0, -1, 0);


  // Update and draw all particles.
  for (let p of particles) {
    p.update();
    p.drawTrail();
    p.display();
  }

  // Draw the inner cylindrical container.
  // We use noFill and a translucent stroke.
  push();
  noFill();
  stroke(255, 100);
  strokeWeight(2);
  // p5.js draws cylinder centered at origin.
  // Use a slight rotation so that the open sides are visible.
  cylinder(cylRadius, cylHeight);
  pop();

  // Draw the outer spherical container.
  push();
  noFill();
  stroke(255, 100);
  strokeWeight(2);
  sphere(sphereRadius);
  pop();

  pop();
}

// The Particle class represents a single ball.
class Particle {
  constructor() {
    // Place the particle randomly inside the cylinder.
    // We choose a random angle and radius (within cylRadius) for x/z,
    // and a random y between -cylHeight/2 and cylHeight/2.
    let angle = random(TWO_PI);
    let rad = random(cylRadius * 0.8); // keep a margin so it's not right on the wall
    this.pos = createVector(rad * cos(angle), random(-cylHeight / 2 * 0.8, cylHeight / 2 * 0.8), rad * sin(angle));
    // Give it a random velocity.
    this.vel = p5.Vector.random3D();
    this.vel.mult(random(5, 10));
    // Store a trail of positions (limit trail length)
    this.trail = [];
    this.maxTrail = 50;
    // Assign a random color for this particle.
    this.col = color(random(50, 255), random(50, 255), random(50, 255));
    // Particle radius (for drawing)
    this.size = 8;
  }

  update() {
    // Save the current position to the trail.
    this.trail.push(this.pos.copy());
    if (this.trail.length > this.maxTrail) {
      this.trail.shift();
    }

    // Update position using current velocity.
    this.pos.add(this.vel);

    // Check collision with the cylindrical side walls.
    // The wall is defined by x^2 + z^2 = cylRadius^2.
    let distXZ = sqrt(this.pos.x * this.pos.x + this.pos.z * this.pos.z);
    if (distXZ > cylRadius - this.size/2) {
      // Calculate the normal vector on the cylinder wall.
      let normal = createVector(this.pos.x, 0, this.pos.z).normalize();
      // Reflect the velocity vector about this normal.
      let dot = this.vel.dot(normal);
      // Only reflect if the particle is moving outwards.
      if (dot > 0) {
        let reflection = p5.Vector.mult(normal, 2 * dot);
        this.vel.sub(reflection);
        // Move the particle back onto the boundary.
        this.pos = p5.Vector.sub(this.pos, p5.Vector.mult(normal, (distXZ - (cylRadius - this.size/2))));
      }
    }

    // Check collision with the top and bottom caps.
    if (this.pos.y > cylHeight / 2 - this.size/2) {
      if (this.vel.y > 0) {
        this.vel.y *= -1;
        this.pos.y = cylHeight / 2 - this.size/2;
      }
    } else if (this.pos.y < -cylHeight / 2 + this.size/2) {
      if (this.vel.y < 0) {
        this.vel.y *= -1;
        this.pos.y = -cylHeight / 2 + this.size/2;
      }
    }
  }

  // Draw the trail of the particle.
  drawTrail() {
    noFill();
    stroke(this.col);
    strokeWeight(2);
    beginShape();
    for (let pos of this.trail) {
      vertex(pos.x, pos.y, pos.z);
    }
    endShape();
  }

  // Draw the particle as a small sphere.
  display() {
    push();
    translate(this.pos.x, this.pos.y, this.pos.z);
    noStroke();
    ambientMaterial(this.col);
    sphere(this.size);
    pop();
  }
}

// Adjust canvas size if the window is resized.
function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}
