import "Lib.helper";

void main(varying float rIn, varying float gIn, varying float bIn,
          output varying float rOut, output varying float gOut, output varying float bOut)
{
    rOut = rIn * kScale; gOut = gIn * kScale; bOut = bIn * kScale;
}
