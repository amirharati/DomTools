/*
DOM Snapshot Utility
-------------------
A browser console utility to capture a complete snapshot of the DOM.
This tool:
- Captures all accessible DOM nodes and their properties
- Handles special cases (SVG, Canvas, Blob, etc.)
- Converts functions to strings
- Captures Shadow DOM
- Provides detailed statistics
- Saves result as downloadable JSON

Usage:
1. Copy this code into browser console
2. Run: dumpDOM() or dumpDOM(maxDepth)
3. Get JSON file and console stats
*/

/**
 * Dumps the full DOM of the current page into a JSON snapshot.
 * @param {number} maxDepth - Maximum depth to traverse the DOM tree (default: 1000).
 * @returns {Object} - A JSON-serializable snapshot of the DOM.
 */
function dumpFullDOM(maxDepth = 1000) {
    // Stats tracking
    const stats = {
        totalNodes: 0,
        nodeTypes: {},
        maxDepthReached: 0,
        errors: 0,
        customElements: 0,
        functions: 0,
        binaryData: 0,
        svgElements: 0
    };

    /**
     * Recursively captures a snapshot of a DOM node.
     * @param {Node} node - The DOM node to snapshot.
     * @param {number} currentDepth - Current depth in the DOM tree.
     * @returns {Object} - A JSON-serializable representation of the node.
     */
    async function snapshot(node, currentDepth = 0) {
        stats.totalNodes++;
        stats.maxDepthReached = Math.max(stats.maxDepthReached, currentDepth);

        // Stop if max depth is reached
        if (currentDepth >= maxDepth) {
            return {
                _maxDepthReached: true,
                nodeName: String(node.nodeName || 'UNKNOWN'),
                nodeType: Number(node.nodeType || 0)
            };
        }

        // Track node type
        const nodeType = Number(node.nodeType || 0);
        stats.nodeTypes[nodeType] = (stats.nodeTypes[nodeType] || 0) + 1;

        // Base result with guaranteed properties
        const result = {
            nodeName: String(node.nodeName || 'UNKNOWN'),
            nodeType: nodeType,
            children: []
        };

        try {
            // Check for custom elements
            if (node.nodeType === 1 && node.nodeName.includes('-')) {
                stats.customElements++;
            }

            // Get ALL properties of the node
            const props = Object.getOwnPropertyNames(node);
            for (const prop of props) {
                try {
                    const value = node[prop];

                    // Handle null values
                    if (value === null) {
                        result[prop] = null;
                        continue;
                    }

                    // Handle different types of values
                    switch (typeof value) {
                        case 'function':
                            stats.functions++;
                            result[prop] = {
                                _type: 'function',
                                source: value.toString()
                            };
                            break;

                        case 'object':
                            // Handle special objects
                            if (value instanceof ImageData) {
                                stats.binaryData++;
                                result[prop] = {
                                    _type: 'ImageData',
                                    width: value.width,
                                    height: value.height,
                                    data: Array.from(value.data)
                                };
                            } else if (value instanceof Blob) {
                                stats.binaryData++;
                                // Asynchronously read Blob data
                                try {
                                    const dataUrl = await readBlobAsDataURL(value);
                                    result[prop] = {
                                        _type: 'Blob',
                                        data: dataUrl
                                    };
                                } catch (e) {
                                    result[prop] = {
                                        _type: 'Blob',
                                        error: e.message
                                    };
                                }
                            } else if (value instanceof SVGElement) {
                                stats.svgElements++;
                                result[prop] = {
                                    _type: 'SVG',
                                    outerHTML: value.outerHTML,
                                    attributes: Array.from(value.attributes || []).map(attr => ({
                                        name: attr.name,
                                        value: attr.value
                                    }))
                                };
                            } else {
                                // Handle other objects
                                try {
                                    JSON.stringify(value); // Check if serializable
                                    result[prop] = value;
                                } catch (e) {
                                    result[prop] = {
                                        _type: 'UnserializableObject',
                                        constructor: value.constructor?.name,
                                        toString: String(value)
                                    };
                                }
                            }
                            break;

                        default:
                            result[prop] = value;
                    }
                } catch (e) {
                    stats.errors++;
                    result[`${prop}_error`] = e.message;
                }
            }

            // Handle canvas elements
            if (node instanceof HTMLCanvasElement) {
                try {
                    stats.binaryData++;
                    result._canvasData = node.toDataURL();
                } catch (e) {
                    stats.errors++;
                    result._canvasError = e.message;
                }
            }

            // Handle child nodes
            if (node.hasChildNodes && node.hasChildNodes()) {
                try {
                    for (const child of Array.from(node.childNodes)) {
                        try {
                            result.children.push(await snapshot(child, currentDepth + 1));
                        } catch (e) {
                            stats.errors++;
                            result.children.push({
                                _error: e.message,
                                nodeName: 'ERROR',
                                nodeType: -1
                            });
                        }
                    }
                } catch (e) {
                    stats.errors++;
                    result._childrenError = e.message;
                }
            }

            // Handle shadow DOM
            if (node.shadowRoot) {
                try {
                    result.shadowRoot = await snapshot(node.shadowRoot, currentDepth + 1);
                } catch (e) {
                    stats.errors++;
                    result._shadowRootError = e.message;
                }
            }
        } catch (e) {
            stats.errors++;
            result._error = e.message;
        }

        return result;
    }

    /**
     * Reads a Blob as a Data URL (asynchronously).
     * @param {Blob} blob - The Blob to read.
     * @returns {Promise<string>} - A Data URL representing the Blob.
     */
    function readBlobAsDataURL(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = () => reject(new Error('Failed to read Blob'));
            reader.readAsDataURL(blob);
        });
    }

    // Start the dump
    (async () => {
        try {
            console.log('Starting DOM snapshot...');
            const startTime = performance.now();

            // Capture the DOM snapshot
            const domSnapshot = await snapshot(document.documentElement);
            const jsonString = JSON.stringify(domSnapshot, null, 2);

            // Log stats
            const endTime = performance.now();
            console.log('\nDOM Snapshot Stats:');
            console.log('==================');
            console.log(`Total nodes processed: ${stats.totalNodes}`);
            console.log(`Maximum depth reached: ${stats.maxDepthReached}`);
            console.log(`Custom elements found: ${stats.customElements}`);
            console.log(`Functions captured: ${stats.functions}`);
            console.log(`Binary data elements: ${stats.binaryData}`);
            console.log(`SVG elements: ${stats.svgElements}`);
            console.log(`Errors encountered: ${stats.errors}`);
            console.log('\nNode types distribution:');
            Object.entries(stats.nodeTypes).forEach(([type, count]) => {
                const typeName = {
                    1: 'ELEMENT_NODE',
                    3: 'TEXT_NODE',
                    8: 'COMMENT_NODE',
                    9: 'DOCUMENT_NODE',
                    10: 'DOCUMENT_TYPE_NODE',
                    11: 'DOCUMENT_FRAGMENT_NODE'
                }[type] || `TYPE_${type}`;
                console.log(`  ${typeName}: ${count}`);
            });
            console.log(`\nTotal processing time: ${(endTime - startTime).toFixed(2)}ms`);

            // Create downloadable link
            const blob = new Blob([jsonString], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `dom-snapshot-${Date.now()}.json`;

            // Trigger download
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);

            return domSnapshot;
        } catch (e) {
            console.error('Failed to dump DOM:', e);
            return {
                error: e.message,
                stack: e.stack
            };
        }
    })();
}

// Make it available in the console
window.dumpDOM = dumpFullDOM;