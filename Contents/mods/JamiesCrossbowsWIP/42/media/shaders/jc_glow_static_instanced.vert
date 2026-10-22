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


layout (location = 0) in vec4 vertex;
layout (location = 1) in vec4 normal;
layout (location = 2) in vec2 uv;

out vec3 vertColour;
out vec3 vertNormal;
out vec2 texCoords;

uniform mat4 ModelViewProjection;

DECLARE_INSTANCING_VERT

BEGIN_INSTANCING

vec3 LightDirection[5];

vec3 LightColour[5];

mat4 MatrixPalette[60];

mat4 transform;
mat4 mvp;

vec2 UVScale;   // 2
float targetDepth;    // 1
float DepthBias;      // 1

vec3 TintColour;
float HighResDepthMultiplier; // 0.5 when drawing models to double-sized chunk textures

vec3 AmbientColour;
float Alpha;

float LightingAmount;
float HueChange;
bool FlipNormal;	// is model inside out?

END_INSTANCING

void main()
{
	COPY_INSTANCE_ID

	GET_INSTANCED_STRUCT(inst);

	vec4 position = vec4(vertex.xyz, 1.0);
	vec4 normal = vec4(normal.xyz, 0.0);

	if (inst.FlipNormal)
		normal = -normal;

	normal = inst.transform * normal;

	vertColour = vec3(1.0);
	vertNormal = normal.xyz;
	texCoords = uv * inst.UVScale * inst.textureSize / TextureDimensions;

	position = inst.mvp * inst.transform * position;

	vec4 origin = inst.mvp * inst.transform * vec4(0, 0, 0, 1);
	position.z += (origin.z - position.z) * inst.HighResDepthMultiplier;
    position.z += inst.targetDepth * 2.0 - 1.0;

	gl_Position = position;
}
