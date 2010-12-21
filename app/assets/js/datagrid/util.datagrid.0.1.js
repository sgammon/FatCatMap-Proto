function truncate(p, len) {
  if (p.length > len) {
    p = p.substring(0, len);
    p = p.replace(/\w+$/, '');
    p += '...';
    return p;
  }
  else
  {	return p;
}
}