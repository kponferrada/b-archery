#version 110
// Jamie's Crossbows - jc_glow (copy of Jamie's Treasures' jt_glow): basicEffect (42.21) + emissive glow column (u >= 0.75). (from Jamie's Treasures dev/make_shaders.py).

varying vec3 vertColour; 
varying vec3 vertNormal;
varying vec2 texCoords;

uniform sampler2D Texture;
uniform float Alpha;
uniform float LightingAmount;

uniform vec3 TintColour;

uniform vec3 AmbientColour;
uniform vec3 Light0Direction;
uniform vec3 Light0Colour;
uniform vec3 Light1Direction;
uniform vec3 Light1Colour;
uniform vec3 Light2Direction;
uniform vec3 Light2Colour;
uniform vec3 Light3Direction;
uniform vec3 Light3Colour;
uniform vec3 Light4Direction;
uniform vec3 Light4Colour;
uniform float HueChange;

// --- inlined from media/shaders/util/math.glsl (42.21), only what hueShift needs ---
vec3 rgb2hsv(vec3 c)
{
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec3 hsv2rgb(vec3 c)
{
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}
// ---

// --- inlined from media/shaders/util/hueShift.glsl (42.21) ---
vec3 hueShift(vec3 col, float amount)
{
    vec3 col3 = rgb2hsv(col);
    col3.r += amount;
    while (col3.r > 1.0)
    {
        col3.r -= 2.0;
    }
    while (col3.r < -1.0)
    {
        col3.r += 2.0;
    }
    return hsv2rgb(col3);
}
// ---


void main()
{
	vec3 normal = normalize(vertNormal);

	vec4 texSample = texture2D(Texture, texCoords);

	if(texSample.w < 0.01)
	{
	    discard;
	}

	vec3 col = texSample.xyz;

    float dotprod;
    if(HueChange != 0.0)
    {
        col = hueShift(col, HueChange);
    }

	const float QuantiseLevels = 8.0;
	vec3 lighting = vec3(0.0);

	dotprod = max(dot(normal, normalize(Light0Direction)), 0.0);
	
	lighting += Light0Colour * dotprod;

	dotprod = max(dot(normal, normalize(Light1Direction)), 0.0);
	
	lighting += Light1Colour * dotprod;

	dotprod = max(dot(normal, normalize(Light2Direction)), 0.0);
	
	lighting += Light2Colour * dotprod;

	dotprod = max(dot(normal, normalize(Light3Direction)), 0.0);
	
	lighting += Light3Colour * dotprod;

	dotprod = max(dot(normal, normalize(Light4Direction)), 0.0);
	
	lighting += Light4Colour * dotprod;

	lighting += AmbientColour;
	lighting.x = min(lighting.x, 1.0);
	lighting.y = min(lighting.y, 1.0);
	lighting.z = min(lighting.z, 1.0);

	vec3 tintColour = TintColour;
	col = vec3(col.x * tintColour.x * lighting.x, col.y * tintColour.y * lighting.y, col.z * tintColour.z * lighting.z);

    vec4 fragCol = vec4(Alpha * col * vertColour, Alpha * texSample.w);
    // jc_glow: the glow column ignores the scene light (emissive surface)
    if (texCoords.x >= 0.75)
    {
        fragCol = vec4(Alpha * texSample.xyz * TintColour, Alpha);
    }
	gl_FragColor = fragCol;
}
