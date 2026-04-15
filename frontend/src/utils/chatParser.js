/**
 * Chat Response Parser
 * Parses numbered restaurant recommendations from bot plain-text responses
 * into structured data for rendering as recommendation cards.
 */

/**
 * Attempt to extract restaurant recommendations from bot text.
 * Returns an array of structured objects if recommendations are detected,
 * or null if the text is a regular message.
 *
 * @param {string} botText - Raw bot_response text
 * @returns {{ intro: string, restaurants: Array, followUp: string|null } | null}
 */
export function parseRecommendations(botText) {
  if (!botText || typeof botText !== 'string') return null;

  // Must contain numbered items to be considered recommendations
  const hasNumberedItems = /\d+\.\s+\S+/.test(botText);
  if (!hasNumberedItems) return null;

  // Must contain at least one recommendation marker
  const hasMarkers = /Rating:|Kecocokan:|Jenis masakan:|Lokasi:|Harga:/i.test(botText);
  if (!hasMarkers) return null;

  const lines = botText.split('\n');

  // Extract intro text (everything before the first numbered item)
  let introLines = [];
  let firstItemIndex = -1;

  for (let i = 0; i < lines.length; i++) {
    if (/^\s*\d+\.\s+/.test(lines[i])) {
      firstItemIndex = i;
      break;
    }
    introLines.push(lines[i]);
  }

  if (firstItemIndex === -1) return null;

  const intro = introLines.join('\n').trim();

  // Split into blocks by numbered items (1. , 2. , etc.)
  const itemBlocks = [];
  let currentBlock = [];

  for (let i = firstItemIndex; i < lines.length; i++) {
    const line = lines[i];
    // A new numbered item starts a new block
    if (/^\s*\d+\.\s+/.test(line) && currentBlock.length > 0) {
      itemBlocks.push(currentBlock);
      currentBlock = [line];
    } else {
      currentBlock.push(line);
    }
  }
  if (currentBlock.length > 0) {
    itemBlocks.push(currentBlock);
  }

  const restaurants = [];
  let followUpLines = [];

  for (const block of itemBlocks) {
    const parsed = parseRestaurantBlock(block);
    if (parsed) {
      restaurants.push(parsed);
    } else {
      // Non-parseable block after restaurants → follow-up text
      followUpLines.push(...block);
    }
  }

  if (restaurants.length === 0) return null;

  // Collect any trailing follow-up text after last restaurant block
  // (e.g., "Mau cari di lokasi tertentu? Ada budget khusus?")
  const lastRestIdx = findLastRestaurantBlockEnd(lines, firstItemIndex);
  if (lastRestIdx < lines.length - 1) {
    const remaining = lines.slice(lastRestIdx + 1).join('\n').trim();
    if (remaining && !followUpLines.length) {
      followUpLines = [remaining];
    }
  }

  const followUp = followUpLines.join('\n').trim() || null;

  return { intro, restaurants, followUp };
}

/**
 * Find the line index where the last restaurant block ends
 */
function findLastRestaurantBlockEnd(lines, startFrom) {
  let lastItemStart = startFrom;
  for (let i = startFrom; i < lines.length; i++) {
    if (/^\s*\d+\.\s+/.test(lines[i])) {
      lastItemStart = i;
    }
  }

  // Walk forward from the last item start to find where it ends
  // (next blank line after content, or end of array)
  let end = lastItemStart;
  let foundContent = false;
  for (let i = lastItemStart; i < lines.length; i++) {
    const trimmed = lines[i].trim();
    if (trimmed.length > 0) {
      foundContent = true;
      end = i;
    } else if (foundContent) {
      // Hit an empty line after content
      break;
    }
  }
  return end;
}

/**
 * Parse a single restaurant text block (array of lines) into structured data.
 */
function parseRestaurantBlock(lines) {
  if (!lines || lines.length === 0) return null;

  // First line: "1. Restaurant Name" or "  1. Restaurant Name"
  const firstLine = lines[0].trim();
  const nameMatch = firstLine.match(/^\d+\.\s+(.+)$/);
  if (!nameMatch) return null;

  const name = nameMatch[1].trim();

  let rating = null;
  let matchPercentage = null;
  let description = null;
  let cuisine = null;
  let location = null;
  let priceRange = null;
  let isPreferred = false;

  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    // Rating line: "Rating: 4.5/5.0 | Kecocokan: 85%"
    const ratingMatch = line.match(/Rating:\s*([\d.]+)\/5/i);
    if (ratingMatch) {
      rating = parseFloat(ratingMatch[1]);
    }

    // Match percentage
    const matchMatch = line.match(/Kecocokan:\s*(\d+)%/i);
    if (matchMatch) {
      matchPercentage = parseInt(matchMatch[1], 10);
    }

    // Preference match
    if (/preferensi/i.test(line) || /Sangat sesuai/i.test(line)) {
      isPreferred = true;
    }

    // Cuisine: "Jenis masakan: ['Seafood', 'Barbecue']" or "Jenis masakan: Italian, Seafood"
    const cuisineMatch = line.match(/Jenis masakan:\s*(.+)/i);
    if (cuisineMatch) {
      let raw = cuisineMatch[1].trim();
      // Clean Python list format: ['a', 'b'] → a, b
      raw = raw.replace(/[\[\]']/g, '').trim();
      cuisine = raw;
      continue;
    }

    // Location: "Lokasi: Kuta Lombok"
    const locationMatch = line.match(/Lokasi:\s*(.+)/i);
    if (locationMatch) {
      location = locationMatch[1].trim();
      continue;
    }

    // Price: "Harga: $$ - $$$"
    const priceMatch = line.match(/Harga:\s*(.+)/i);
    if (priceMatch) {
      priceRange = priceMatch[1].trim();
      continue;
    }

    // Skip rating/kecocokan lines for description detection
    if (ratingMatch || matchMatch) continue;

    // Skip personal recommendation reason lines
    if (/👉|cocok untuk|sesuai dengan|Anda suka/i.test(line)) continue;

    // Skip follow-up questions
    if (/Mau cari|Ada budget|Untuk acara|Butuh info|kriteria|Atau/i.test(line)) continue;

    // Remaining lines longer than 15 chars are descriptions
    // (addresses, about text, etc.)
    if (line.length > 15 && !description) {
      description = line.length > 120 ? line.slice(0, 120) + '…' : line;
    }
  }

  // Only return if we got at least a name and some data
  if (!rating && !cuisine && !location) return null;

  return {
    name,
    rating,
    matchPercentage,
    description,
    cuisine,
    location,
    priceRange,
    isPreferred,
  };
}

export default parseRecommendations;
