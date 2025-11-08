export function getSuffix(rsrc_suffix?: string) {
  if (rsrc_suffix === undefined) {
    throw new Error("Context parameter 'stackSuffix' is required. Pass it with '-c stackSuffix=yourSuffix'.");
  }
  return rsrc_suffix ? `-${rsrc_suffix}` : ''
}
