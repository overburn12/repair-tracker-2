import { useState } from 'react';

/**
 * SearchBox - Input with button for adding entities
 */
export default function SearchBox({ placeholder, onAdd, buttonText = 'Add' }) {
  const [value, setValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.trim()) {
      onAdd(value.trim());
      setValue('');
    }
  };

  return (
    <form className="search-box" onSubmit={handleSubmit}>
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
      />
      <button type="submit">{buttonText}</button>
    </form>
  );
}
