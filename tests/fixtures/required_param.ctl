void main(varying float rIn, varying float gIn, varying float bIn,
          float scale,
          output varying float rOut, output varying float gOut, output varying float bOut)
{
    rOut = rIn * scale; gOut = gIn * scale; bOut = bIn * scale;
}
