#version 430 core
// Jamie's Crossbows - jc_glow (copy of Jamie's Treasures' jt_glow): basicEffect (42.21) + emissive glow column (u >= 0.75). (from Jamie's Treasures dev/make_shaders.py).

// --- inlined from media/shaders/util/instancing.h (42.21) ---
#define INSTANCE_MAX 128
#define TEXTURE_UNIFORMS uniform sampler2DArray InstTexArr; uniform vec2 TextureDimensions;
#define INSTANCE_TEXTURE_VARS vec2 textureSize; int textureIndex;
#define INSTANCE_BUFFER_DATA InstancedStruct instancedStructs[INSTANCE_MAX];
#define DECLARE_INSTANCING_VERT flat out int instanceID; TEXTURE_UNIFORMS
#define DECLARE_INSTANCING_FRAG flat in int instanceID; TEXTURE_UNIFORMS
#define BEGIN_INSTANCING struct InstancedStruct { INSTANCE_TEXTURE_VARS
#define END_INSTANCING }; layout (std430) buffer instancedData { INSTANCE_BUFFER_DATA };
#define COPY_INSTANCE_ID instanceID = gl_InstanceID;
#define GET_INSTANCED_STRUCT(name) InstancedStruct name = instancedStructs[instanceID];
#define TRANSFORM_UV(uv, inst) uv * inst.textureSize / TextureDimensions;
#define SAMPLE_TEXTURE_ARRAY(uv, inst) texture(InstTexArr, vec3(uv, inst.textureIndex));
#define INSTANCED_ARG(name) InstancedStruct name
// ---


in vec3 vertColour;
in vec3 vertNormal;
in vec2 texCoords;

out vec4 colour;

DECLARE_INSTANCING_FRAG

BEGIN_INSTANCING

vec3 LightDirection[5];

vec3 LightColour[5];

mat4 MatrixPalette[60];

mat4 transform;
mat4 mvp;

vec2 UVScale;
float targetDepth;
float DepthBias;

vec3 TintColour;
float HighResDepthMultiplier; // 0.5 when drawing models to double-sized chunk textures

vec3 AmbientColour;
float Alpha;

float LightingAmount;
float HueChange;
bool FlipNormal;

END_INSTANCING

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
	GET_INSTANCED_STRUCT(inst);

	vec3 normal = normalize(vertNormal);

	vec4 texSample = SAMPLE_TEXTURE_ARRAY(texCoords, inst);

	if (texSample.w < 0.01)
	    discard;

	vec3 col = texSample.xyz;

    if (inst.HueChange != 0.0)
        col = hueShift(col, inst.HueChange);

	const float QuantiseLevels = 8.0;
	vec3 lighting = vec3(0.0);

    for (int i = 0; i < 5; i++)
    {
	    vec3 dir = normalize(inst.LightDirection[i]);
	    float dotProd = max(dot(normal, dir), 0.0);
	    lighting += inst.LightColour[i] * dotProd;
    }

	lighting += inst.AmbientColour;
	lighting = min(lighting, vec3(1.0));

	col = col * inst.TintColour * lighting;

	colour = vec4(col * vertColour, texSample.w) * inst.Alpha;
	// jc_glow: texCoords are scaled into the texture array; undo that to get the model's own u
	float jtU = texCoords.x * TextureDimensions.x / max(inst.textureSize.x, 1.0);
	if (jtU >= 0.75)
	{
	    colour = vec4(texSample.xyz * inst.TintColour, 1.0) * inst.Alpha;
	}
}
